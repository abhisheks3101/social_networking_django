## Social Networking APIs Overview

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/abhisheks3101/social_networking_django.git
   ```

2. **Create and activate virtual environment:**
   - For macOS/Linux:
     ```bash
     pip install virtualenv     # Install virtualenv
     virtualenv venv             # Create virtual env named 'venv'
     source venv/bin/activate    # Activate virtualenv
     ```
   - For Windows (cmd):
     ```bash
     pip install virtualenv     # Install virtualenv
     virtualenv venv             # Create virtual env named 'venv'
     venv\Scripts\activate       # Activate virtualenv
     ```

3. **Install dependencies:**
   ```bash
   pip install -r req.txt
   ```

4. **Configure Environment Variables:**
   - Create a `.env` file in the project root directory and define necessary variables like database credentials, secret key, etc.

### APIs

#### User Registration

- **Endpoint:** `/user/register/`
- **Method:** POST
- **Description:** Register a new user account.
- **Required Fields:** username, email, password
- **Returns:** Token for authentication in subsequent requests.

#### User Login

- **Endpoint:** `/user/login/`
- **Method:** POST
- **Description:** Log in with username and password to obtain authentication token.
- **Required Fields:** username, password
- **Returns:** Token for authentication in subsequent requests.

#### User Detail

- **Endpoint:** `/user/detail/`
- **Method:** GET
- **Description:** Retrieve detailed information about the logged-in user.
- **Authentication:** Token required in headers.

#### User Search

- **Endpoint:** `/user/search/`
- **Method:** GET
- **Description:** Search for users by username or email.
- **Query Parameters:** `query` (search query string)
- **Authentication:** Token required in headers.

#### Send Friend Request

- **Endpoint:** `/user/friend-requests/`
- **Method:** POST
- **Description:** Send a friend request to another user.
- **Required Fields:** receiver_id (ID of the user to send the request to)
- **Authentication:** Token required in headers.

#### Respond to Friend Request

- **Endpoint:** `/user/friend-request/<uuid:pk>/`
- **Method:** PUT
- **Description:** Accept or reject a friend request.
- **URL Parameter:** pk (ID of the friend request)
- **Request Body:** status ("accepted" or "rejected")
- **Authentication:** Token required in headers.

#### Pending Friend Requests

- **Endpoint:** `/user/friend-requests-pending/`
- **Method:** GET
- **Description:** Retrieve pending friend requests sent to the logged-in user.
- **Authentication:** Token required in headers.

#### User Friends List

- **Endpoint:** `/user/friends-list/`
- **Method:** GET
- **Description:** Retrieve list of friends for the logged-in user.
- **Authentication:** Token required in headers.
