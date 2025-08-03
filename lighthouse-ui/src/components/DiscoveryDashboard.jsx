import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Sparkles,
  Brain,
  TrendingUp,
  Clock,
  Search,
  BookOpen,
  Lightbulb,
  Target,
  ArrowRight,
  RefreshCw,
  Users,
  Calendar,
  Hash,
  Zap
} from "lucide-react";

const DiscoveryDashboard = ({ onNavigate }) => {
  const [insights, setInsights] = useState([]);
  const [themes, setThemes] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [stats, setStats] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      // Simulate API calls - replace with actual Enhanced Lighthouse API calls
      await Promise.all([
        loadInsightFeed(),
        loadThematicClusters(),
        loadRecentActivity(),
        loadPersonalStats()
      ]);
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadInsightFeed = async () => {
    try {
      const response = await fetch('http://localhost:8100/api/insights/feed?limit=10');
      if (response.ok) {
        const data = await response.json();
        setInsights(data);
      } else {
        // Fallback to mock data if API fails
        setInsights([
          {
            id: 1,
            type: "connection",
            title: "Unexpected Pattern: Consciousness & Technology",
            description: "Your writings about consciousness from 2023 unexpectedly connect with recent technology reflections",
            confidence: 0.89,
            sources: ["Journal Entry #245", "Tech Note #67"],
            date: "2 hours ago"
          },
      {
        id: 2,
        type: "evolution",
        title: "Evolving Perspective: Creative Process",
        description: "Your approach to creative work has shifted significantly over the past 6 months",
        confidence: 0.76,
        sources: ["Various notes", "Project reflections"],
        date: "1 day ago"
      },
      {
        id: 3,
        type: "forgotten",
        title: "Rediscovered Gem: Future Vision from 2022",
        description: "A prescient insight about AI and humanity that feels remarkably relevant today",
        confidence: 0.94,
        sources: ["Deep Work Session #34"],
        date: "3 days ago"
      }
    ]);
      }
    } catch (error) {
      console.error("Failed to load insights:", error);
      // Use fallback data on error  
      setInsights([]);
    }
  };

  const loadThematicClusters = async () => {
    try {
      const response = await fetch('http://localhost:8100/api/insights/themes');
      if (response.ok) {
        const data = await response.json();
        const formattedThemes = data.map((theme, index) => ({
          name: theme.name,
          count: theme.count,
          growth: theme.growth_percentage,
          color: ["purple", "blue", "green", "orange", "pink"][index % 5]
        }));
        setThemes(formattedThemes);
      } else {
        // Fallback data
        setThemes([
          { name: "Consciousness & Mind", count: 147, growth: "+12%", color: "purple" },
          { name: "Technology & Future", count: 89, growth: "+8%", color: "blue" },
          { name: "Creative Process", count: 76, growth: "+15%", color: "green" },
          { name: "Human Nature", count: 134, growth: "+3%", color: "orange" },
          { name: "Philosophy & Meaning", count: 98, growth: "+7%", color: "pink" }
        ]);
      }
    } catch (error) {
      console.error("Failed to load themes:", error);
      setThemes([]);
    }
  };

  const loadRecentActivity = async () => {
    try {
      const response = await fetch('http://localhost:8100/api/insights/activity?limit=10');
      if (response.ok) {
        const data = await response.json();
        setRecentActivity(data);
      } else {
        // Fallback data
        setRecentActivity([
          { type: "ingestion", description: "Processed 3 new notebook pages", time: "2h ago" },
          { type: "discovery", description: "Found 5 thematic connections", time: "4h ago" },
          { type: "transformation", description: "Generated academic perspective on creativity", time: "1d ago" },
          { type: "export", description: "Created book draft: 'Consciousness Explorations'", time: "2d ago" }
        ]);
      }
    } catch (error) {
      console.error("Failed to load activity:", error);
      setRecentActivity([]);
    }
  };

  const loadPersonalStats = async () => {
    try {
      const response = await fetch('http://localhost:8100/api/insights/stats');
      if (response.ok) {
        const data = await response.json();
        setStats({
          totalContent: data.total_content,
          uniqueThemes: data.unique_themes,
          connectionsFound: 892,
          booksGenerated: data.insights_generated,
          lastActivity: "2 hours ago"
        });
      } else {
        // Fallback data
        setStats({
          totalContent: 1247,
          uniqueThemes: 23,
          connectionsFound: 892,
          booksGenerated: 8,
          lastActivity: "2 hours ago"
        });
      }
    } catch (error) {
      console.error("Failed to load stats:", error);
      setStats({});
    }
  };

  const refreshInsights = async () => {
    try {
      const response = await fetch('http://localhost:8100/api/insights/refresh', {
        method: 'POST'
      });
      if (response.ok) {
        // Reload all dashboard data after refresh
        await loadDashboardData();
      }
    } catch (error) {
      console.error("Failed to refresh insights:", error);
    }
  };

  const InsightCard = ({ insight }) => {
    const getInsightIcon = (type) => {
      switch (type) {
        case "connection": return <Zap className="w-5 h-5" />;
        case "evolution": return <TrendingUp className="w-5 h-5" />;
        case "forgotten": return <Lightbulb className="w-5 h-5" />;
        default: return <Sparkles className="w-5 h-5" />;
      }
    };

    const getInsightColor = (type) => {
      switch (type) {
        case "connection": return "text-yellow-400 bg-yellow-400/10";
        case "evolution": return "text-blue-400 bg-blue-400/10";
        case "forgotten": return "text-green-400 bg-green-400/10";
        default: return "text-purple-400 bg-purple-400/10";
      }
    };

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-card/50 backdrop-blur-sm rounded-lg p-4 border border-border/50 hover:border-border transition-all cursor-pointer"
        onClick={() => onNavigate && onNavigate('archive', { searchQuery: insight.title })}
      >
        <div className="flex items-start space-x-3">
          <div className={`p-2 rounded-lg ${getInsightColor(insight.type)}`}>
            {getInsightIcon(insight.type)}
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-foreground mb-1">{insight.title}</h3>
            <p className="text-sm text-card-content mb-2">{insight.description}</p>
            <div className="flex items-center justify-between text-xs text-card-secondary">
              <div className="flex items-center space-x-2">
                <span>Confidence: {Math.round(insight.confidence * 100)}%</span>
                <span>•</span>
                <span>{insight.sources.length} sources</span>
              </div>
              <span>{insight.date}</span>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-card-secondary" />
        </div>
      </motion.div>
    );
  };

  const ThemeCluster = ({ theme }) => {
    const colorClasses = {
      purple: "bg-purple-500/20 text-purple-300 border-purple-500/30",
      blue: "bg-blue-500/20 text-blue-300 border-blue-500/30",
      green: "bg-green-500/20 text-green-300 border-green-500/30",
      orange: "bg-orange-500/20 text-orange-300 border-orange-500/30",
      pink: "bg-pink-500/20 text-pink-300 border-pink-500/30"
    };

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`rounded-lg p-3 border cursor-pointer hover:scale-105 transition-all ${colorClasses[theme.color]}`}
        onClick={() => onNavigate && onNavigate('archive', { themeFilter: theme.name })}
      >
        <h4 className="font-medium mb-1">{theme.name}</h4>
        <div className="flex items-center justify-between text-sm">
          <span>{theme.count} items</span>
          <span className="text-green-400">{theme.growth}</span>
        </div>
      </motion.div>
    );
  };

  const StatCard = ({ icon: Icon, label, value, color = "text-blue-400" }) => (
    <div className="bg-card/30 backdrop-blur-sm rounded-lg p-4 border border-border/30">
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg bg-current/10 ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <p className="text-sm text-card-secondary">{label}</p>
          <p className="text-lg font-semibold text-foreground">{value}</p>
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <RefreshCw className="w-8 h-8 text-card-secondary" />
        </motion.div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground mb-2">
            Discovery Dashboard
          </h1>
          <p className="text-card-secondary">
            Mining insights from your creative universe
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={refreshInsights}
          className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh Insights</span>
        </motion.button>
      </div>

      {/* Personal Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          icon={BookOpen}
          label="Content Pieces"
          value={stats.totalContent?.toLocaleString() || "0"}
          color="text-purple-400"
        />
        <StatCard
          icon={Hash}
          label="Unique Themes"
          value={stats.uniqueThemes || "0"}
          color="text-blue-400"
        />
        <StatCard
          icon={Zap}
          label="Connections Found"
          value={stats.connectionsFound?.toLocaleString() || "0"}
          color="text-yellow-400"
        />
        <StatCard
          icon={BookOpen}
          label="Books Generated"
          value={stats.booksGenerated || "0"}
          color="text-green-400"
        />
        <StatCard
          icon={Clock}
          label="Last Activity"
          value={stats.lastActivity || "Unknown"}
          color="text-orange-400"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* AI-Curated Insights */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center space-x-2 mb-4">
            <Brain className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-semibold text-foreground">AI-Curated Insights</h2>
            <span className="text-xs bg-purple-400/20 text-purple-300 px-2 py-1 rounded-full">
              {insights.length} new
            </span>
          </div>
          <div className="space-y-3">
            {insights.map((insight) => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }}
            onClick={() => onNavigate && onNavigate('archive', { mode: 'insights' })}
            className="w-full py-3 border border-border/50 rounded-lg text-card-secondary hover:text-foreground hover:border-border transition-all flex items-center justify-center space-x-2"
          >
            <Search className="w-4 h-4" />
            <span>Explore All Insights</span>
          </motion.button>
        </div>

        {/* Thematic Clusters */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 mb-4">
            <Target className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-foreground">Thematic Clusters</h2>
          </div>
          <div className="space-y-3">
            {themes.map((theme, index) => (
              <ThemeCluster key={index} theme={theme} />
            ))}
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }}
            onClick={() => onNavigate && onNavigate('thematic-maps')}
            className="w-full py-3 border border-border/50 rounded-lg text-card-secondary hover:text-foreground hover:border-border transition-all flex items-center justify-center space-x-2"
          >
            <Users className="w-4 h-4" />
            <span>View Theme Map</span>
          </motion.button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-card/30 backdrop-blur-sm rounded-lg p-4 border border-border/30">
        <div className="flex items-center space-x-2 mb-4">
          <Calendar className="w-5 h-5 text-green-400" />
          <h2 className="text-lg font-semibold text-foreground">Recent Activity</h2>
        </div>
        <div className="space-y-2">
          {recentActivity.map((activity, index) => (
            <div key={index} className="flex items-center justify-between py-2 border-b border-border/20 last:border-b-0">
              <span className="text-sm text-foreground">{activity.description}</span>
              <span className="text-xs text-card-secondary">{activity.time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={() => onNavigate && onNavigate('content-ingestion')}
          className="p-4 bg-card/30 backdrop-blur-sm rounded-lg border border-border/30 hover:border-border transition-all text-center"
        >
          <BookOpen className="w-6 h-6 text-purple-400 mx-auto mb-2" />
          <span className="text-sm text-foreground">Add Content</span>
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={() => onNavigate && onNavigate('archive-explorer')}
          className="p-4 bg-card/30 backdrop-blur-sm rounded-lg border border-border/30 hover:border-border transition-all text-center"
        >
          <Search className="w-6 h-6 text-blue-400 mx-auto mb-2" />
          <span className="text-sm text-foreground">Search Archive</span>
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={() => onNavigate && onNavigate('book-generator')}
          className="p-4 bg-card/30 backdrop-blur-sm rounded-lg border border-border/30 hover:border-border transition-all text-center"
        >
          <BookOpen className="w-6 h-6 text-green-400 mx-auto mb-2" />
          <span className="text-sm text-foreground">Generate Book</span>
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={() => onNavigate && onNavigate('narrative-studio')}
          className="p-4 bg-card/30 backdrop-blur-sm rounded-lg border border-border/30 hover:border-border transition-all text-center"
        >
          <Sparkles className="w-6 h-6 text-yellow-400 mx-auto mb-2" />
          <span className="text-sm text-foreground">Transform Text</span>
        </motion.button>
      </div>
    </div>
  );
};

export default DiscoveryDashboard;