## Local Setup

### Pre-requisites

- Python >= 3.8.10 (Tested with 3.8.10 version. If you have different version of python, please update the pyproject.toml to change python version)
- Poetry >= 1.0.0

### Setup

- Clone the repository to your local
  `git clone https://github.com/Jeevan-J/smart-contract-deployer.git`
- Go to the cloned directory
  `cd smart-contract-deployer`
- Create virtual environment and install dependencies
  `poetry install`
- Create `.env` file with appropriate values from `.env-sample`. You need to [create a INFURA project](https://blog.infura.io/post/getting-started-with-infura-28e41844cc89) and API tokens in respective network block explorers (for example [Etherscan](https://www.youtube.com/watch?v=QDeAQa-75xs) and [Polygonscan](https://www.youtube.com/watch?v=51IC0dZGTbg)) for verification.
- Run and check if brownie networks is working properly. 
  `poetry run brownie networks list`
  If you want to add or update any network, you can do so using [tutorial](https://www.youtube.com/watch?v=toqMi41c-l4)

### Run the API server

- Go to `app` folder
  `cd app`
- Run the API server
  `poetry run uvicorn --host 0.0.0.0 --port 5000 app:app`
- Now go to `http://localhost:5000/docs` to see the API documentation
