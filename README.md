# Project Setup and Usage Instructions

This guide provides clear step-by-step instructions to help you set up and access the project environment.

---

## 📋 Prerequisites

### 1. **Docker Installation**

Install Docker on your machine by following the official guide:

[Docker Installation Guide](https://www.docker.com/get-started)

### 2. **Elasticsearch Setup**

- Download and install [Elasticsearch](https://www.elastic.co/downloads/elasticsearch) locally.
- Ensure Elasticsearch service is running on the default port (`9200`) or a custom port you specify.

### 3. **Upload Dataset**

Download the dataset from [this link](https://drive.google.com/file/d/1GNYjlfCWtUFmCm3kXzfHHgyQBMmC9eEP/view).

Upload the provided dataset into your local Elasticsearch instance using your preferred indexing method.

---

## 🛠 Repository Setup

### 1. **Clone the Repository**

Open your terminal and run:

```bash
git clone https://github.com/flamango04/Foodielicious.git
```

### 2. **Navigate to the Project Directory**

Change your working directory to `real_process`:

```bash
cd real_process
```

---

## ⚙️ Configuration

### 1. **Editing the Configuration (********`app.py`********)**

Open the `app.py` file in your code editor.

### 2. **Update Elasticsearch Credentials**

Find line **109**:

```python
        basic_auth=("elastic", "7KYl8Zpm"),
```

Replace `"elastic"` and `"7KYl8Zpm"` with your own Elasticsearch username and password.

---
### 3. **Hugging Face Access Token**

- Navigate to the official [Hugging Face website](https://huggingface.co.)
- Log in to your account or sign up if you don't have an account
- Navigate to your "Settings" and then go to "Access Tokens"
- Click on the "Create New Token" button, name your token, and select all the role/permissions available
- Generate the token and copy the token 
- Find line **328**
```python
        "Authorization": f"Bearer <huggingface_access_token>"
```
- Paste the token over <huggingface_access_token>

## 🚀 Running the Application

### 1. **Start the Application**

Run the `app.py` file from your terminal:

```bash
python app.py
```

> **Note:** Ensure your Python environment is properly configured and that all necessary dependencies are installed.

### 2. **Accessing the Application**

In your web browser, navigate to:

```bash
http://localhost:9200
```

Your application should now be accessible and fully functional.

---

🎉 **You're all set! Happy coding!**

