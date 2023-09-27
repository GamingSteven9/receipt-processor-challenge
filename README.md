# receipt-processor-challenge

This project was built using Python, HTML, and Flask

# Install:

git clone https://github.com/GamingSteven9/receipt-processor-challenge.git
cd receipt-processor-challenge

Build the docker image:

docker build --tag receipt-processor-challenge .

# Run:

docker run --publish 8000:5000 -t -i receipt-processor-challenge

Open http://localhost:8000/receipts in a browser

# Test:

Insert a JSON receipt

Click the "Generate ID" button to get the ID

Input the ID into the text field

Click the "Get Points" button to get the points