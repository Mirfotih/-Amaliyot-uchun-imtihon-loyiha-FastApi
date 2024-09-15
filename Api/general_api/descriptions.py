create_user_desc_post = """
***POST*** \n
Create User \n
requires: 
- username
- first_name
- last_name
- password
- email
- phone_num
- role
- gender
"""




user_login_desc_post = """
***POST*** \n
User Login \n
requires:
- username
- password

Create Token \n
response:
- access_token
- token_type

"""

user_verifications_desc_post = """
***PUT*** \n
User Verifications (Password Change) \n
requires:
- password
- new_password
"""