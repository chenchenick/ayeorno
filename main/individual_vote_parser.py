from bs4 import BeautifulSoup

class IndividualVoteParser:
    @staticmethod
    def parse_individual_votes(soup):
        votes_tbody = soup.find('tbody', id='member-votes')
        if not votes_tbody:
            print("Warning: Could not find tbody with id 'member-votes'")
            print("This appears to be a different type of vote.")
            return None  # Return None instead of an empty list

        individual_votes = []

        for row in votes_tbody.find_all('tr'):
            vote_data = {}

            # Extract member name and link
            member_link = row.find('a', class_='library-link')
            if member_link:
                vote_data['representative_name'] = member_link.text.strip()
                vote_data['member_link'] = member_link['href']
            else:
                member_td = row.find('td', {'data-label': 'member'})
                vote_data['representative_name'] = member_td.text.strip() if member_td else 'N/A'
                vote_data['member_link'] = 'N/A'

            # Extract party
            party_td = row.find('td', {'data-label': 'party'})
            vote_data['party'] = party_td.text.strip() if party_td else 'N/A'

            # Extract state (prefer full state name)
            state_td_full = row.find('td', {'data-label': 'state', 'class': 'hidden-sm hidden-xs'})
            state_td_abbr = row.find('td', {'data-label': 'state', 'class': 'visible-sm visible-xs'})
            vote_data['state'] = state_td_full.text.strip() if state_td_full else (state_td_abbr.text.strip() if state_td_abbr else 'N/A')

            # Extract vote
            vote_td = row.find('td', {'data-label': 'vote'})
            vote_data['vote'] = vote_td.text.strip() if vote_td else 'N/A'

            individual_votes.append(vote_data)

        print(f"Parsed {len(individual_votes)} individual votes")
        if individual_votes:
            print("Sample of parsed votes:")
            print(individual_votes[:5])  # Print first 5 parsed votes

        return individual_votes