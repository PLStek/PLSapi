# PLSres API

![GitHub](https://img.shields.io/github/license/PLStek/PLSapi)
![GitHub repo size](https://img.shields.io/github/repo-size/PLStek/PLSapi)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/PLStek/PLSapi)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-pr/PLStek/PLSapi)

This is a FastAPi backend for the PLSres Angular app. It allows the centralization of teaching resources linked to the PL$tek project.

## Prerequisites

Before you begin, ensure you have the following prerequisites installed and set up:

- Python 3 and pip installed
- An SQL database
- A Youtube API key
- A Discord app with the redirect URL correctly configured

## Installation and Setup

Clone the repository and navigate to the project directory:

```bash
git clone --recursive https://github.com/PLStek/PLSapi.git
cd PLSapi
```

Install requirements:

```bash
pip install -r requirements.txt
```

Rename `.env.example` to `.env` and replace the values with your own.

## Running the app

To run the app using uvicorn, use the following command:

```bash
uvicorn main:app --reload
```
