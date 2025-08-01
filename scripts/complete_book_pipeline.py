#!/usr/bin/env python3
"""
Complete Book Production Pipeline
Fully automated workflow from insights to refined books
"""

import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

class CompleteBookPipeline:
    """Complete automated book production pipeline"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path.cwd()
        self.base_dir = Path(base_dir)
        self.output_dir = self.base_dir / "complete_book_production"
        self.output_dir.mkdir(exist_ok=True)
        
        print("📚 Complete Book Production Pipeline")
        print("=" * 50)
        print(f"📂 Working directory: {self.base_dir}")
        print(f"📂 Output directory: {self.output_dir}")
    
    def run_book_factory(self, quality_threshold: float = 0.3, dry_run: bool = False) -> bool:
        """Run the automated book factory"""
        print("\n🏭 Phase 1: Automated Book Generation")
        print("-" * 40)
        
        cmd = ["haw", "book-factory", "--quality-threshold", str(quality_threshold)]
        if dry_run:
            cmd.append("--dry-run")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                print("✅ Book factory completed successfully")
                if not dry_run:
                    print("📚 Books generated in automated_books/ directory")
                return True
            else:
                print(f"❌ Book factory failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error running book factory: {e}")
            return False
    
    def run_book_editor(self) -> bool:
        """Run the AI book editor"""
        print("\n🤖 Phase 2: AI Editorial Refinement")
        print("-" * 40)
        
        try:
            result = subprocess.run(["haw", "book-editor"], 
                                  capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                print("✅ AI editorial refinement completed")
                print("📋 Editorial outlines and refined books created")
                return True
            else:
                print(f"❌ Book editor failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error running book editor: {e}")
            return False
    
    def generate_production_summary(self) -> str:
        """Generate final production summary"""
        summary_path = self.output_dir / "production_summary.md"
        
        # Count generated files
        books_dir = self.base_dir / "automated_books"
        refined_dir = books_dir / "refined"
        
        original_books = list(books_dir.glob("book_*.md")) if books_dir.exists() else []
        refined_books = list(refined_dir.glob("*_auto_refined.md")) if refined_dir.exists() else []
        editorial_outlines = list(refined_dir.glob("*_editorial_outline.md")) if refined_dir.exists() else []
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# Complete Book Production Summary\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            f.write("## Production Results\n\n")
            f.write(f"- **Original Books Generated:** {len(original_books)}\n")
            f.write(f"- **AI-Refined Books:** {len(refined_books)}\n")
            f.write(f"- **Editorial Outlines:** {len(editorial_outlines)}\n\n")
            
            if original_books:
                f.write("### Original Books\n")
                for book in original_books:
                    f.write(f"- `{book.name}`\n")
                f.write("\n")
            
            if refined_books:
                f.write("### AI-Refined Books (Ready for Review)\n")
                for book in refined_books:
                    f.write(f"- `{book.name}`\n")
                f.write("\n")
            
            if editorial_outlines:
                f.write("### Editorial Outlines\n")
                for outline in editorial_outlines:
                    f.write(f"- `{outline.name}`\n")
                f.write("\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. **Review AI-Refined Books**: Quality check the automatically improved versions\n")
            f.write("2. **Apply Editorial Outlines**: Use detailed recommendations for manual refinement\n")
            f.write("3. **Final Editorial Pass**: Human review and polishing\n")
            f.write("4. **Publication Formatting**: Prepare for final publication format\n\n")
            
            f.write("## Quality Metrics\n\n")
            if refined_books:
                total_words = 0
                for book in refined_books:
                    try:
                        with open(book, 'r', encoding='utf-8') as bf:
                            content = bf.read()
                            words = len(content.split())
                            total_words += words
                            f.write(f"- **{book.stem}**: ~{words:,} words\n")
                    except:
                        f.write(f"- **{book.stem}**: Unable to count words\n")
                
                f.write(f"\n**Total Content**: ~{total_words:,} words across {len(refined_books)} books\n\n")
            
        return str(summary_path)
    
    def run_complete_pipeline(self, quality_threshold: float = 0.3, 
                            dry_run: bool = False) -> bool:
        """Run the complete pipeline"""
        print("🚀 Starting Complete Book Production Pipeline")
        print("=" * 60)
        
        success = True
        
        # Phase 1: Generate books
        if not self.run_book_factory(quality_threshold, dry_run):
            success = False
        
        # Phase 2: Editorial refinement (only if books were generated)
        if success and not dry_run:
            if not self.run_book_editor():
                success = False
        
        # Phase 3: Generate summary
        if success and not dry_run:
            print("\n📋 Phase 3: Production Summary")
            print("-" * 40)
            summary_path = self.generate_production_summary()
            print(f"✅ Production summary: {summary_path}")
        
        # Final results
        print(f"\n🎉 Pipeline {'Simulation' if dry_run else 'Execution'} Complete!")
        if success:
            if dry_run:
                print("✅ Dry run successful - ready for production")
            else:
                print("✅ Books generated and refined successfully")
                print(f"📂 Check outputs in: {self.output_dir}")
        else:
            print("❌ Pipeline encountered errors")
        
        return success

def main():
    parser = argparse.ArgumentParser(description="Complete Book Production Pipeline")
    parser.add_argument('--quality-threshold', type=float, default=0.3,
                       help='Quality threshold for insight selection (0.0-1.0)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulate the pipeline without generating files')
    parser.add_argument('--base-dir', help='Base directory for operations')
    
    args = parser.parse_args()
    
    try:
        pipeline = CompleteBookPipeline(args.base_dir)
        success = pipeline.run_complete_pipeline(
            quality_threshold=args.quality_threshold,
            dry_run=args.dry_run
        )
        
        if success:
            print("\n🎯 Pipeline completed successfully!")
            if not args.dry_run:
                print("\n📚 Your 7 books are ready for review:")
                print("   1. Original generated versions")
                print("   2. AI-refined versions with improvements")
                print("   3. Editorial outlines for further refinement")
        else:
            print("\n❌ Pipeline failed - check error messages above")
            
    except KeyboardInterrupt:
        print("\n👋 Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()