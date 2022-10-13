"""
API Server for Solidity Smart Contract Deployment using Brownie
"""

import os
from typing import Optional

from fastapi import FastAPI, APIRouter, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathvalidate import validate_filename, ValidationError

import brownie
from brownie import accounts, project, network
from brownie._cli import pm as package_manager

load_dotenv("../.env")

app = FastAPI()

if os.getenv("ENABLE_CORS", "False") == "True":
    origins = os.getenv("CORS_ORIGINS").split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# CONSTANTS
CONTRACT_TEMPLATE_FOLDER = "../templates"
CONTRACT_FOLDER = "../contracts"

# APIs for managing the current account
class ActiveAccount:
    """
    Class for storing ActiveAccount to deploy Smart Contract
    """

    def __init__(self):
        self.account: brownie.network.account = None
        self.account_name = None

    def set_account(self, account: brownie.network.account, account_name: str):
        """
        Set active account and it's name

        Args:
            account (brownie.network.account): Loaded account
            account_name (str): account name
        """
        self.account = account
        self.account_name = account_name

    def get_account_info(self):
        """
        Return current active account information

        Returns:
            json: JSON with account name and address
        """
        return {
            "account_name": self.account_name,
            "account_address": self.account.address,
        }


ACTIVEACCOUNT = ActiveAccount()

account_router = APIRouter(prefix="/accounts", tags=["Accounts"])


@account_router.get("/")
def get_accounts_list():
    """
    Return list of available wallet accounts to deploy smart contract

    Returns:
        json: Accounts list
    """
    return {"accounts": accounts.load()}


@account_router.get("/active")
def get_account_active():
    """
    Return active account to deploy smart contract

    Returns:
        json: Active Account address
    """
    if ACTIVEACCOUNT.account:
        return {
            "status": "ok",
            "active": True,
            "account": ACTIVEACCOUNT.get_account_info(),
        }
    return {"status": "ok", "active": False}


@account_router.post("/set_active")
def set_account_active(account_name: str, account_pass: str):
    """
    Set active account

    Args:
        account_name (str): Account name
        account_pass (str): Account password

    Returns:
        json: account information
    """
    try:
        account = accounts.load(account_name, account_pass)
        # change_account(account, account_name)
        ACTIVEACCOUNT.set_account(account, account_name)
        return {
            "status": "ok",
            "active": True,
            "account_name": account_name,
            "account_address": account.address,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@account_router.get("/generate")
def generate_new_account(
    account_name: str, account_pass: str, private_key: Optional[str] = None
):
    """
    Generate a new account

    Args:
        private_key (str): private key of any wallet

    Returns:
        json: new account information
    """
    account = accounts.add(private_key=private_key)
    if account_pass:
        account.save(filename=account_name, password=account_pass)
    return {
        "status": "ok",
        "account_address": account.address,
        "account_private_key": account.private_key,
    }


# Not working as expected
@account_router.delete("/delete")
def delete_account(account_name: str, account_pass: str):
    """
    Delete an account using address

    Args:
        account_name (str): account name
        account_pass (str): account password

    Returns:
        json: status
    """
    try:
        account = accounts.load(account_name, account_pass)
    except Exception as exc:
        return HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": f'No account found locally with name "{account_name}". {str(exc)}',
            },
        )
    accounts.remove(account)


app.include_router(account_router)

# API router for networks

network_router = APIRouter(prefix="/network", tags=["Network"])


@network_router.get("/active")
def get_network_active():
    """
    Return active network

    Returns:
        json: JSON with active network if connected
    """
    if network.is_connected():
        return {"status": "ok", "network": network.show_active()}
    return {"status": "error", "message": "Not connected to any network"}


@network_router.get("/set")
def set_network_active(network_name: str):
    """
    Connects to specified network if available

    Args:
        network_name (str): network name to connect

    Returns:
        json: JSON with active network if connected
    """
    if network.is_connected():
        network.disconnect()
    network.connect(network_name)
    return {"status": "ok", "network": network.show_active()}


app.include_router(network_router)

# API router for Templates

template_router = APIRouter(prefix="/templates", tags=["Templates"])


@template_router.get("/")
def get_templates_list():
    """
    Returns list of available templates

    Returns:
        json: list of available templates
    """
    return {
        "status": "ok",
        "templates": [
            template_name.split(".sol")[0]
            for template_name in os.listdir(CONTRACT_TEMPLATE_FOLDER)
            if template_name.endswith(".sol")
        ],
    }


@template_router.get("/code")
def get_template_code(template_name: str):
    """
    Returns the template solidity code

    Args:
        template_name (str): template name

    Returns:
        json: Solidity code
    """
    if not template_name.endswith(".sol"):
        template_name += ".sol"
    try:
        validate_filename(template_name)
        template_path = os.path.join(CONTRACT_TEMPLATE_FOLDER, template_name)
        if os.path.exists(template_path):
            return {
                "status": "ok",
                "template_name": template_name,
                "template_code": open(template_path, "r", encoding="utf-8").read(),
            }
        return {"status": "error", "message": f'template "{template_name}" not found'}
    except ValidationError as exc:
        return {"status": "error", "message": f"{exc}"}


@template_router.post("/add")
def add_template(template_name: str, template_bytes: bytes = File(...)):
    """
    Creates a new template with solidity code

    Args:
        template_name (str): template name
        template_bytes (str): template bytes

    Returns:
        json: template name
    """
    if not template_name.endswith(".sol"):
        template_name += ".sol"
    try:
        validate_filename(template_name)
        template_path = os.path.join(CONTRACT_TEMPLATE_FOLDER, template_name)
        if os.path.exists(template_path):
            return {
                "status": "error",
                "message": f'template "{template_name}" already exists',
            }
        with open(template_path, "wb") as template_file:
            template_file.write(template_bytes)
        return {"status": "ok", "template_name": template_name}
    except ValidationError as exc:
        return {"status": "error", "message": f"{exc}"}


@template_router.delete("/delete")
def delete_template(template_name: str):
    """
    Creates a new template with solidity code

    Args:
        template_name (str): template name
        template_code (str): template code

    Returns:
        json: template name
    """
    if not template_name.endswith(".sol"):
        template_name += ".sol"
    try:
        validate_filename(template_name)
        template_path = os.path.join(CONTRACT_TEMPLATE_FOLDER, template_name)
        if not os.path.exists(template_path):
            return {
                "status": "error",
                "message": f'template "{template_name}" not found',
            }
        try:
            os.remove(template_path)
            return {"status": "ok", "template_name": template_name}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}
    except ValidationError as exc:
        return {"status": "error", "message": f"{exc}"}


app.include_router(template_router)

# API for Deployment of Smart Contracts

deployment_router = APIRouter(prefix="/deploy", tags=["Deployment"])


@deployment_router.post("/template")
def deploy_template_contract(
    template_name: str,
    template_params: dict,
    contract_name: str,
    publish_source: bool = True,
):
    """
    Deploy a Smart Contract using pre-defined ERC Templates

    Args:
        template_name (str): Template name
        template_params (dict): key-value pairs of parameters
        contract_name (str): contract name (same as TOKEN_NAME)

    Returns:
        json: Returns a JSON with status and deployed contract information
    """
    try:
        if not template_name.endswith(".sol"):
            template_name += ".sol"
        contract_path = contract_name + ".sol"
        validate_filename(template_name)
        validate_filename(contract_path)
        template_path = os.path.join("../templates/", template_name)
        contract_path = os.path.join("../contracts/", contract_path)
        if not os.path.exists(template_path):
            return {
                "status": "error",
                "message": f"{template_name} template is not available!",
            }
        with open(template_path, "r", encoding="utf-8") as template:
            template_code = template.read()
            for key, value in template_params.items():
                template_code = template_code.replace("<" + key + ">", value)
            with open(contract_path, "w+", encoding="utf-8") as contract_file:
                contract_file.write(template_code)
        contract_proj = project.load("../")
        contract_container = contract_proj[contract_name]
        try:
            deployed_contract = contract_container.deploy(
                {"from": ACTIVEACCOUNT.account}, publish_source=publish_source
            )
            contract_json = {
                "data": {
                    "abi": contract_container.abi,
                    "contract": template_code,
                    "network": network.show_active(),
                    "verification_info": contract_container.get_verification_info(),
                    "deployed_bytecode": deployed_contract.bytecode,
                    "contract_name": contract_name,
                    "contract_params": template_params,
                    "contract_code": template_code,
                    "contract_address": deployed_contract.address,
                    "deployer_address": ACTIVEACCOUNT.account.address,
                },
                "status": "success",
            }
            contract_proj.close()
            return contract_json
        except Exception as exc:
            contract_proj.close()
            return {"status": "error","message": f"{str(exc)}"}
    except KeyError as exc:
        return {
            "status": "error",
            "message": f"Please make sure that the contract name and token name are same! KeyError: {str(exc)}",
        }
    except ValidationError as exc:
        return {"status": "error", "message": f"{exc}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


app.include_router(deployment_router)

# API for Smart Contracts

contract_router = APIRouter(prefix="/contracts", tags=["Contract"])


@contract_router.get("/")
def get_contracts():
    """
    Returns the contracts

    Returns:
        list: contracts list
    """
    contract_proj = project.load("../")
    return {"status": "ok", "contracts": list(contract_proj.keys())}


@contract_router.post("/interact")
def interact_contract(
    contract_name: str, contract_address: str, contract_method: str, method_args: tuple
):
    """
    Interact with a Smart Contract using pre-defined ERC Templates

    Args:
        contract_name (str): contract name (same as TOKEN_NAME)
        contract_address (dict): deployed contract address
        contract_method (str): contract method
        method_args (tuple): contract method arguments

    Returns:
        json: Returns a JSON with status and transaction information
    """
    try:
        contract_proj = project.load("../")
        contract_container = contract_proj[contract_name]
        deployed_contract = contract_container.at(contract_address)
        func = deployed_contract.get_method_object(
            deployed_contract.signatures[contract_method]
        )
        func_tx = func.transact(*method_args, {"from": ACTIVEACCOUNT.account})
        contract_proj.close()
        return {
            "status": "success",
            "tx_hash": func_tx.txid,
            "tx_status": func_tx.status,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


app.include_router(contract_router)


# API for Brownie Package Manager
pm_router = APIRouter(prefix="/pm", tags=["Package Manager"])


@pm_router.post("/delete")
def pm_delete(package_name: str):
    """
    Delete brownie packages

    Args:
        package_name (str): Package Name

    Returns:
        json: Returns a JSON with status
    """
    try:
        package_manager._delete(package_name)
        return {"status": "success", "message": f"{package_name} deleted successfully"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@pm_router.post("/install")
def pm_install(package_name: str):
    """
    Install brownie packages

    Args:
        package_name (str): Package Name

    Returns:
        json: Returns a JSON with status
    """
    try:
        package_manager._install(package_name)
        return {
            "status": "success",
            "message": f"{package_name} installed successfully",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

app.include_router(pm_router)
