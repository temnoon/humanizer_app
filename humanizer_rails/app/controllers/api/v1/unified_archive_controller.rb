# frozen_string_literal: true

module Api
  module V1
    # Unified Archive Controller
    # Provides Rails API access to the unified PostgreSQL archive
    class UnifiedArchiveController < ApplicationController
      before_action :set_content, only: [:show, :update, :destroy, :thread, :enhance]
      before_action :validate_search_params, only: [:search]

      # GET /api/v1/unified_archive
      def index
        @content = ArchivedContent.all
        @content = apply_filters(@content)
        @content = @content.page(params[:page]).per(params[:per_page] || 50)

        render json: {
          content: @content.map(&:summary),
          pagination: pagination_meta(@content),
          statistics: ArchivedContent.statistics
        }
      end

      # GET /api/v1/unified_archive/search
      def search
        query = params[:query]
        options = {
          source_types: params[:source_types]&.split(','),
          content_types: params[:content_types]&.split(','),
          author: params[:author],
          date_from: parse_date(params[:date_from]),
          date_to: parse_date(params[:date_to]),
          limit: params[:limit]&.to_i || 50,
          offset: params[:offset]&.to_i || 0
        }

        @results = ArchivedContent.search_unified(query, options)
        
        render json: {
          results: @results.map(&:summary),
          count: @results.size,
          query: query,
          filters_applied: options.compact,
          total_archive_size: ArchivedContent.count
        }
      end

      # GET /api/v1/unified_archive/:id
      def show
        render json: {
          content: @content.export_data,
          related_content: @content.related_content.map(&:summary),
          conversation_context: conversation_context(@content)
        }
      end

      # GET /api/v1/unified_archive/:id/thread
      def thread
        thread_messages = @content.conversation_thread
        
        render json: {
          conversation_id: @content.parent_id || @content.id,
          total_messages: thread_messages.count,
          participants: @content.conversation_participants,
          messages: thread_messages.map(&:summary),
          timeline: thread_timeline(thread_messages)
        }
      end

      # POST /api/v1/unified_archive/:id/enhance
      def enhance
        @content.enhance_with_lpe!
        
        render json: {
          message: 'Enhancement started',
          content_id: @content.id,
          status: @content.processing_status
        }
      end

      # GET /api/v1/unified_archive/statistics
      def statistics
        stats = ArchivedContent.statistics
        
        render json: {
          archive_statistics: stats,
          top_authors: ArchivedContent.top_authors,
          content_by_date: ArchivedContent.content_by_date,
          quality_distribution: quality_distribution,
          source_health: source_health_check
        }
      end

      # GET /api/v1/unified_archive/sources
      def sources
        sources = ArchivedContent.group(:source_type).count.map do |source_type, count|
          {
            source_type: source_type,
            content_count: count,
            latest_content: ArchivedContent.where(source_type: source_type).recent.first&.timestamp,
            processing_status: ArchivedContent.where(source_type: source_type).group(:processing_status).count
          }
        end

        render json: {
          sources: sources,
          total_sources: sources.size
        }
      end

      # POST /api/v1/unified_archive/import
      def import
        import_type = params[:import_type]
        source_path = params[:source_path]
        
        case import_type
        when 'node_archive'
          import_result = import_node_archive(source_path)
        when 'social_media'
          import_result = import_social_media(source_path)
        else
          return render json: { error: 'Unsupported import type' }, status: :bad_request
        end

        render json: import_result
      end

      # GET /api/v1/unified_archive/export
      def export
        format = params[:format] || 'json'
        filters = {
          source_types: params[:source_types]&.split(','),
          content_types: params[:content_types]&.split(','),
          date_from: parse_date(params[:date_from]),
          date_to: parse_date(params[:date_to])
        }

        content = ArchivedContent.all
        content = apply_export_filters(content, filters)

        case format
        when 'json'
          render json: {
            exported_at: Time.current.iso8601,
            content_count: content.count,
            content: content.limit(1000).map(&:export_data) # Limit for memory
          }
        when 'csv'
          send_data generate_csv(content), filename: "archive_export_#{Date.current}.csv"
        when 'writebook'
          writebook_data = content.limit(100).map(&:to_writebook_section)
          render json: {
            writebook_export: writebook_data,
            section_count: writebook_data.size
          }
        else
          render json: { error: 'Unsupported export format' }, status: :bad_request
        end
      end

      # GET /api/v1/unified_archive/authors
      def authors
        authors = ArchivedContent
          .where.not(author: [nil, ''])
          .group(:author)
          .order('count_id DESC')
          .limit(params[:limit] || 50)
          .count(:id)

        author_details = authors.map do |author, count|
          latest_content = ArchivedContent.where(author: author).recent.first
          {
            author: author,
            content_count: count,
            latest_content_at: latest_content&.timestamp,
            source_types: ArchivedContent.where(author: author).distinct.pluck(:source_type),
            average_quality: ArchivedContent.where(author: author).average(:content_quality_score)&.round(3)
          }
        end

        render json: {
          authors: author_details,
          total_authors: ArchivedContent.distinct.count(:author)
        }
      end

      # GET /api/v1/unified_archive/timeline
      def timeline
        date_from = parse_date(params[:date_from]) || 30.days.ago
        date_to = parse_date(params[:date_to]) || Time.current
        
        timeline_data = ArchivedContent
          .where(timestamp: date_from..date_to)
          .group_by_day(:timestamp)
          .group(:source_type)
          .count

        formatted_timeline = timeline_data.map do |(date, source_type), count|
          {
            date: date.to_date,
            source_type: source_type,
            content_count: count
          }
        end

        render json: {
          timeline: formatted_timeline,
          date_range: "#{date_from.to_date} to #{date_to.to_date}",
          total_content: formatted_timeline.sum { |item| item[:content_count] }
        }
      end

      private

      def set_content
        @content = ArchivedContent.find(params[:id])
      rescue ActiveRecord::RecordNotFound
        render json: { error: 'Content not found' }, status: :not_found
      end

      def validate_search_params
        # Basic validation for search parameters
        if params[:limit].present? && params[:limit].to_i > 500
          render json: { error: 'Limit cannot exceed 500' }, status: :bad_request
        end
      end

      def apply_filters(content)
        content = content.where(source_type: params[:source_type]) if params[:source_type].present?
        content = content.where(content_type: params[:content_type]) if params[:content_type].present?
        content = content.where(author: params[:author]) if params[:author].present?
        content = content.from_date(parse_date(params[:date_from])) if params[:date_from].present?
        content = content.to_date(parse_date(params[:date_to])) if params[:date_to].present?
        content = content.where(processing_status: params[:status]) if params[:status].present?
        
        content.recent
      end

      def apply_export_filters(content, filters)
        content = content.where(source_type: filters[:source_types]) if filters[:source_types].present?
        content = content.where(content_type: filters[:content_types]) if filters[:content_types].present?
        content = content.from_date(filters[:date_from]) if filters[:date_from].present?
        content = content.to_date(filters[:date_to]) if filters[:date_to].present?
        
        content.recent
      end

      def conversation_context(content)
        if content.is_conversation?
          {
            type: 'conversation_root',
            message_count: content.child_messages.count,
            participants: content.participants
          }
        elsif content.parent_conversation
          {
            type: 'message_in_conversation',
            conversation_id: content.parent_id,
            position_in_thread: content.parent_conversation.child_messages.where('timestamp <= ?', content.timestamp).count
          }
        else
          {
            type: 'standalone_content'
          }
        end
      end

      def thread_timeline(messages)
        return [] if messages.empty?

        start_time = messages.first.timestamp
        messages.map do |message|
          {
            message_id: message.id,
            author: message.author,
            timestamp: message.timestamp&.iso8601,
            offset_minutes: start_time ? ((message.timestamp - start_time) / 1.minute).round : 0,
            word_count: message.word_count
          }
        end
      end

      def quality_distribution
        ArchivedContent
          .where.not(content_quality_score: nil)
          .group('FLOOR(content_quality_score * 10) / 10')
          .count
          .transform_keys { |k| "#{k}-#{k + 0.1}" }
      end

      def source_health_check
        ArchivedContent.group(:source_type).group(:processing_status).count.map do |(source_type, status), count|
          {
            source_type: source_type,
            status: status,
            count: count
          }
        end
      end

      def import_node_archive(source_path)
        # This would trigger the Python import service
        # For now, return a placeholder response
        {
          message: 'Node Archive import initiated',
          source_path: source_path,
          status: 'started',
          estimated_duration: '5-30 minutes'
        }
      end

      def import_social_media(source_path)
        # Placeholder for social media import
        {
          message: 'Social Media import initiated', 
          source_path: source_path,
          status: 'started'
        }
      end

      def generate_csv(content)
        require 'csv'
        
        CSV.generate do |csv|
          csv << ['ID', 'Source Type', 'Content Type', 'Author', 'Title', 'Word Count', 'Quality Score', 'Timestamp']
          
          content.find_each do |item|
            csv << [
              item.id,
              item.source_type,
              item.content_type, 
              item.author,
              item.title,
              item.word_count,
              item.content_quality_score,
              item.timestamp&.iso8601
            ]
          end
        end
      end

      def parse_date(date_string)
        return nil if date_string.blank?
        Date.parse(date_string)
      rescue ArgumentError
        nil
      end

      def pagination_meta(collection)
        {
          current_page: collection.current_page,
          total_pages: collection.total_pages,
          total_count: collection.total_count,
          per_page: collection.limit_value
        }
      end
    end
  end
end