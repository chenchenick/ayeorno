class VoteParser:
    @staticmethod
    def parse_vote_data(soup):
        # Extract key information
        og_title = soup.find("meta", {"property": "og:title"})["content"]
        roll_call = og_title.split("Roll Call ")[1].split(",")[0] if "Roll Call " in og_title else "N/A"
        
        # Handle case where bill number might not be present
        bill_number = "N/A"
        if "Bill Number: " in og_title:
            bill_number = og_title.split("Bill Number: ")[1].split(",")[0]
        
        # Find the date and time of the vote
        date_time = soup.find("meta", {"property": "article:published_time"})["content"]
        
        # Session details are part of the 'og:title' or header information
        session = og_title.split(", ")[-1] if ", " in og_title else "N/A"
        
        # Vote question and description
        twitter_description = soup.find("meta", {"name": "twitter:description"})["content"]
        vote_question = twitter_description.split(", DESCRIPTION:")[0].replace("VOTE QUESTION: ", "") if ", DESCRIPTION:" in twitter_description else twitter_description
        vote_description = twitter_description.split(", DESCRIPTION:")[1].split(", VOTE TYPE:")[0] if ", DESCRIPTION:" in twitter_description and ", VOTE TYPE:" in twitter_description else "N/A"
        
        # Extract vote type and status
        vote_type = twitter_description.split("VOTE TYPE: ")[1].split(", STATUS:")[0] if "VOTE TYPE: " in twitter_description and ", STATUS:" in twitter_description else "N/A"
        status = twitter_description.split(", STATUS: ")[1] if ", STATUS: " in twitter_description else "N/A"
        
        # Find the vote counts (Yea, Nay, Present, Not Voting)
        vote_table = soup.find_all("div", class_="col-xs-6 col-md-3")
        yea_count = int(vote_table[0].find("p", class_="number").text.strip()) if len(vote_table) > 0 else 0
        nay_count = int(vote_table[1].find("p", class_="number").text.strip()) if len(vote_table) > 1 else 0
        present_count = int(vote_table[2].find("p", class_="number").text.strip()) if len(vote_table) > 2 else 0
        not_voting_count = int(vote_table[3].find("p", class_="number").text.strip()) if len(vote_table) > 3 else 0
        
        # Create a dictionary to store the parsed data
        vote_data = {
            "roll_call": roll_call,
            "bill_number": bill_number,
            "date_time": date_time,
            "session": session,
            "vote_question": vote_question,
            "vote_description": vote_description,
            "vote_type": vote_type,
            "status": status,
            "votes": {
                "yea": yea_count,
                "nay": nay_count,
                "present": present_count,
                "not_voting": not_voting_count
            }
        }
        
        # Return the vote data
        return vote_data