import os
from pathlib import Path
from db_handler import DBHandler
from countvotes import process_vote_file

def count_votes():
    base_folder = Path("vote_records")
    db = DBHandler()
    
    total_votes = 0
    processed_votes = 0
    failed_votes = 0

    for year_folder in sorted(base_folder.iterdir(), reverse=True):
        if year_folder.is_dir():
            year = int(year_folder.name)
            year_votes = 0
            year_processed = 0
            year_failed = 0

            for vote_file in sorted(year_folder.glob("*.html")):
                total_votes += 1
                year_votes += 1
                
                try:
                    process_vote_file(str(vote_file))
                    processed_votes += 1
                    year_processed += 1
                except Exception as e:
                    print(f"Failed to process {vote_file}: {str(e)}")
                    failed_votes += 1
                    year_failed += 1

            # Save year summary to database
            db.insert_year_summary(year, year_votes, year_processed, year_failed)
            
            print(f"Year {year}: Total votes: {year_votes}, Processed: {year_processed}, Failed: {year_failed}")

    # Save overall summary to database
    db.insert_overall_summary(total_votes, processed_votes, failed_votes)
    
    print(f"\nOverall Summary:")
    print(f"Total votes: {total_votes}")
    print(f"Processed votes: {processed_votes}")
    print(f"Failed votes: {failed_votes}")

    db.close()

if __name__ == "__main__":
    count_votes()