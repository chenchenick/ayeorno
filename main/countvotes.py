import sys
from bs4 import BeautifulSoup
from db_handler import DBHandler
from vote_parser_ai import VoteParserAI
from individual_vote_parser import IndividualVoteParser

def process_vote_file(file_path):
    print(f"Processing file: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")
        print(f"HTML content length: {len(html_content)} characters")

        print("Parsing vote data...")
        vote_data = VoteParserAI.parse_vote_data(soup)
        if not vote_data:
            print("No vote data found. Skipping this file.")
            return

        print("Vote data parsed successfully:")
        print(vote_data)

        print("Parsing individual votes...")
        individual_votes = IndividualVoteParser.parse_individual_votes(soup)
        
        if individual_votes is None:
            print("This is not a member-votes type. Marking as 'other' and skipping individual vote data.")
            vote_data['vote_type'] = 'other'
        else:
            print(f"Found {len(individual_votes)} individual votes")

        print("Inserting data into database...")
        db = DBHandler()
        vote_id = db.insert_vote(
            date=vote_data['date_time'],
            congress=vote_data['session'],
            question=vote_data['vote_question'],
            bill_description=vote_data['vote_description'],
            vote_type=vote_data['vote_type'],
            status=vote_data['status'],
            roll_call=vote_data['roll_call'],
            bill_number=vote_data['bill_number'],
            session=vote_data['session'],
            yea_count=vote_data['votes']['yea'],
            nay_count=vote_data['votes']['nay'],
            present_count=vote_data['votes']['present'],
            not_voting_count=vote_data['votes']['not_voting']
        )

        if individual_votes:
            for vote in individual_votes:
                db.insert_individual_vote(
                    vote_id, 
                    vote.get('member_link', 'N/A'),
                    vote.get('representative_name', 'N/A'),
                    vote.get('vote', 'N/A'),
                    vote.get('party', 'N/A'),
                    vote.get('state', 'N/A')
                )

        db.close()
        print("Data saved to the local database.")
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        file_path = 'vote_records/2023/2023_0001.html'
        print("No argument provided, using default file path.")
    else:
        file_path = sys.argv[1]
    process_vote_file(file_path)
