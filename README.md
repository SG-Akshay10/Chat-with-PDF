# Chat-with-PDF

An advanced RAG-based app to chat with large PDFs (500+ pages), supporting multi-turn conversations and deep-dive Q&amp;A with source-cited answers. Built with FastAPI, vector search, and LLMs via Vertex AI.

## Local Setup and Quick Demo

This guide will walk you through setting up the application locally and provide quick commands to get you started.

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.x: For the backend.

- pip: Python package installer (usually comes with Python).

- Node.js and npm: For the frontend.

### Local Setup

Follow these steps to get the application running on your local machine:

1. Clone the Repository (if you haven't already):
```
git clone <your-repository-url>
cd <your-repository-name>
```

2. Backend Setup:

-   Navigate into the backend directory:

    ```
    cd backend
    ```

-   Install the required Python dependencies:
    
    ```
    pip install -r requirements.txt
    ```

-   Start the backend server:
    ```
    uvicorn main:app --reload --port 8000
    ```

This command will start the backend server, typically accessible at `http://127.0.0.1:8000` or `http://localhost:8000`. The `--reload` flag ensures that the server automatically reloads when you make changes to the code.

3. Frontend Setup:

-   Open a new terminal window and navigate into the frontend directory:
    ```
    cd frontend
    ```

-   Install the necessary Node.js dependencies:
    ```
    npm install
    ```

-   Start the frontend application:
    ```
    npm start
    ```

This will launch the frontend development server. You'll be able to access the application in your web browser, typically at `http://localhost:3000/`.

Local Setup and Quick Demo

This guide will walk you through setting up the application locally and provide quick commands to get you started.

Prerequisites

Before you begin, ensure you have the following installed:

    Python 3.x: For the backend.

    pip: Python package installer (usually comes with Python).

    Node.js and npm: For the frontend.

Local Setup

Follow these steps to get the application running on your local machine:

    Clone the Repository (if you haven't already):
    Bash

git clone <your-repository-url>
cd <your-repository-name>

Backend Setup:

    Navigate into the backend directory:
    Bash

cd backend

Install the required Python dependencies:
Bash

pip install -r requirements.txt

Start the backend server:
Bash

    uvicorn main:app --reload --port 8000

    This command will start the backend server, typically accessible at http://127.0.0.1:8000 or http://localhost:8000. The --reload flag ensures that the server automatically reloads when you make changes to the code.

Frontend Setup:

    Open a new terminal window and navigate into the frontend directory:
    Bash

cd frontend

Install the necessary Node.js dependencies:
Bash

npm install

Start the frontend application:
Bash

        npm start

        This will launch the frontend development server. You'll be able to access the application in your web browser, typically at http://localhost:3000/.

### Docker Setup (Alternative)

For a more streamlined setup, you can use Docker and Docker Compose:

1.  Build the Docker Images:
    Navigate to the root directory of your project (where the docker-compose.yml file is located) and run:
    ```
    docker compose build
    ```
This command will build the necessary Docker images for both your backend and frontend services.

2.  Start the Application with Docker Compose:
Once the images are built, start the application with:
    ```
    docker compose up
    ```
This command will bring up both the backend and frontend services in isolated containers.

### Quick Demo

Once both the backend and frontend servers are running, you can interact with the application:

1.  Access the Application:
    Open your web browser and go to:
    ```
    http://localhost:3000/
    ```
2.  Upload and Process Documents:

    -   On the application interface, click the "Browse" button to select a PDF document from your local machine.

    -   After selecting your PDF, click the "Process Documents" button to upload it.

    -   You will receive a notification once the document has been successfully uploaded and processed.

3.  Interact with Your PDF:

    -   Once your document is uploaded, you can start interacting with its content directly within the application.


## UI Screenshots

### Document Upload Interface
![Document Upload Screen](/assests/Chat-with-pdf1.png)  
*Initial screen showing model selection and document upload options*

### File Selection
![File Selection Screen](/assests/Chat-with-pdf2.png)

![File Selection Screen](/assests/Chat-with-pdf3.png)
*Interface displaying selected PDF files for processing*


### Successful Processing
![Processing Success Screen](/assests/Chat-with-pdf4.png)  
*Confirmation message after successful document processing*

### Chat Interface
![Active Chat Screen](/assests/Chat-with-pdf6.png)  

![Active Chat Screen](/assests/Chat-with-pdf7.png)  

## Demo Video
[![ChatPDF Demo Video](/assests/Chat-with-pdf1.png)](/assests/demo_video.mkv)  
*Click to watch the application demo video*
