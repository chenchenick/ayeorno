import ollama
import json
from bs4 import BeautifulSoup

class VoteParserAI:
    @staticmethod
    def parse_vote_data(soup):
        # Extract relevant parts of the HTML
        page_detail = soup.find('h1', id='pageDetail')
        role_call_vote = soup.find('div', class_='role-call-vote')

        extracted_content = ""
        if page_detail:
            extracted_content += str(page_detail)
        if role_call_vote:
            extracted_content += str(role_call_vote)

        prompt = f"""
        Nothing else but the JSON object should be returned, or else you will be penalized.
        Parse the following HTML content and extract the vote information. Return a JSON object with the following structure:

        {{
            "roll_call": "string",
            "bill_number": "string",
            "date_time": "string",
            "session": "string",
            "vote_question": "string",
            "vote_description": "string",
            "vote_type": "string",
            "status": "string",
            "votes": {{
                "yea": number,
                "nay": number,
                "present": number,
                "not_voting": number
            }}
        }}

        HTML content:
        {extracted_content}

        Return only the JSON object, no additional text.
        """

        print("Sending request to Ollama...")
        response = ollama.generate(model="llama3.2", prompt=prompt)
        print("Received response from Ollama")
        print("Response type:", type(response))
        #print("Response content:", response)
        print("Response content:", response['response'])
        
        try:
            # Extract the JSON string from the 'response' key
            json_str = response['response']
            
            # Remove any potential markdown formatting
            json_str = json_str.replace('```json', '').replace('```', '').strip()
            
            # Parse the JSON string
            vote_data = json.loads(json_str)

            print("Parsed vote_data:", vote_data)

            # Validate the structure of vote_data
            required_keys = ["roll_call", "bill_number", "date_time", "session", "vote_question", 
                             "vote_description", "vote_type", "status", "votes"]
            if all(key in vote_data for key in required_keys):
                print("All required keys found in vote_data")
                return vote_data
            else:
                print("Error: Incomplete data structure in Ollama response")
                print("Received data:", vote_data)
                return None

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Ollama response: {str(e)}")
            print("JSON string:", json_str)
            return None
        except KeyError as e:
            print(f"KeyError: {str(e)}")
            print("Response does not contain expected 'response' key")
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print("Ollama response:", response)
            return None