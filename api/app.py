from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import brownie
import brownie.project as project

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/simple_nft")
def read_item(nft_name: str, nft_symbol: str , mint_cost: str, max_supply: str, max_mint_amount_per_tx: str, base_uri: str):
    try:
        with open("../templates/SimpleNFT.sol","r") as template:
            template_code = template.read()
            template_code = template_code.replace("<TOKEN_NAME>", nft_name)\
                .replace("<TOKEN_SYMBOL>",nft_symbol)\
                .replace("<MINT_COST>",mint_cost)\
                .replace("<MAX_SUPPLY>",max_supply)\
                .replace("<MAX_MINT_AMOUNT_PER_TX>",max_mint_amount_per_tx)\
                .replace("<BASE_URI>",base_uri)
            with open("../contracts/"+nft_name+".sol","w+") as ct:
                ct.write(template_code)
        a = brownie.compile_source(template_code)
        return {"data":{"abi":a.dict()[nft_name].abi,"bytecode":a.dict()[nft_name].bytecode,"contract":template_code},"status":"success"}
    except Exception as e:
        return {"status":"error","message":str(e)}