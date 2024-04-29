# Hot Topic Timeline Generator

## Project Overview

In today's fast-paced world, social media platforms like Weibo have become central hubs for news dissemination and opinion sharing. However, the rapid influx of information leads to significant challenges, notably information overload. During major news events, user-generated content surges, creating a dense and complex flow of information that can be challenging to navigate and understand comprehensively.

This project addresses these challenges by leveraging advanced technologies to crawl, process, and analyze data from the Weibo platform to construct insightful event timelines. Our primary objective is to capture daily hot topics, analyze the content, and provide users with a clear, chronological view of events as they unfold.

### Goals

- **Data Crawling:** Develop a custom web crawler to collect daily trending topics from Weibo, including posts and associated metadata.
- **Data Processing and Storage:** Utilize robust big data technologies like Hadoop or Spark to manage the volume and complexity of the data.
- **Text Analysis:** Apply advanced text analysis techniques to understand user behavior and topic evolution on Weibo.
- **Machine Learning:** Train machine learning models on distributed systems to enhance the accuracy and efficiency of the timeline generation process.
- **Cloud Integration:** Implement cloud-based solutions to improve the scalability and responsiveness of our system, ensuring that users can access and interact with the timeline seamlessly.

By adopting these methodologies, we aim to mitigate the issue of information overload on Weibo, making it easier for users to grasp the significance of news events without getting lost in the vast sea of information. Our system will provide a valuable tool for both casual users and professionals who rely on timely and accurate information aggregation to make informed decisions.

## Environment Setup

To ensure the successful deployment and operation of our Hot Topic Timeline Generator, specific environment configurations are required. Below is a detailed guide on setting up the environment using Amazon Web Services (AWS), specifically EC2 and S3 services.

### AWS EC2 Configuration

- **Instance Type:** `m5.large`
  - This instance type provides a balance of compute, memory, and networking resources, making it ideal for the medium-scale processing required by our project.

- **Operating System:** Ubuntu
  - **AMI Name:** `ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-20240301`
  - This AMI provides Ubuntu 22.04 LTS, offering a stable and secure environment for our application.

### AWS S3 Configuration

- **Usage:** Storing and retrieving data such as vocabulary lists, weight matrices, and inverted index tables.
- AWS S3 is utilized for its scalability, security, and high availability, which are crucial for handling large volumes of unstructured data generated and processed by our application.

### Local and Remote Development Environment Setup

Ensure that your local development environment matches the production settings as closely as possible. This includes installing necessary software and libraries that are compatible with the AWS EC2 instance.

- **Required Software:**
  - Python 3.8 or higher
  - Apache Hadoop
  - Apache Spark
  - MXNet
  - TensorFlow
  - Additional Python libraries as specified in `requirements.txt`

## Installation Guide

This guide provides detailed steps for setting up and configuring the AWS EC2 instance and necessary software for the Hot Topic Timeline Generator project.

### 1. Connecting EC2 with VSCode Remote SSH

To manage development directly on the AWS EC2 instance, use the VSCode Remote - SSH extension:

- **SSH Configuration:**
  - Save your EC2 SSH key (e.g., `your-ec2-key.pem`) in a safe directory on your local machine:
    ```
    C:/Users/username/.ssh/
    ```
  - Configure SSH to connect to your EC2 instance by editing the SSH config file:
    ```
    C:/Users/username/.ssh/config
    ```
    Add the following configuration:
    ```
    Host aws-ec2
        HostName <your-ec2-ip-address>
        User ubuntu
        IdentityFile ~/.ssh/your-ec2-key.pem
    ```

### 2. Basic Environment Setup on Remote Server

Once connected through SSH, prepare the server environment:
```bash
sudo apt-get update
sudo apt-get install sysbench
sudo apt install python3-pip
```

### 3. Setting up Project Dependencies

Navigate to the project directory and install the required Python dependencies:

```bash
cd TopicTimeline
sudo apt install python3-pip
pip3 install -r requirements.txt
```

#### Handling Missing Chinese Fonts

If running the code results in errors due to missing Chinese fonts, you need to install the font and clear the matplotlib cache:

```bash
sudo cp /home/ubuntu/TopicTimeline/SimHei.ttf /usr/share/fonts/
rm ~/.cache/matplotlib/fontlist-v330.json
rm -rf /home/featurize/.cache/matplotlib
```

### 4. Configuring EC2 and S3 Connectivity

For seamless integration between the EC2 instance and AWS S3, follow these steps:

#### IAM and Role Assignment

1. Create an IAM role with the _AmazonS3FullAccess_ policy.
2. Assign this IAM role to your EC2 instance to facilitate easy access to S3 buckets.

#### Using Boto3 for AWS Services

Install and configure Boto3, a Python library that allows you to directly interact with AWS services:

```bash
pip3 install boto3
```

This setup will ensure that your EC2 instance can efficiently interact with S3, utilizing it for storing and retrieving large datasets necessary for the project.

## Code Execution

To execute the code for the Hot Topic Timeline Generator project, follow the steps below according to the provided file structure and the role of each script in the project.

### Project File Structure Overview

- `add_new_mind.ipynb`: Jupyter notebook used to train the sentiment analysis model using TensorFlow.
- `mxnet_code.py`: Python script for training the sentiment analysis model using MXNet.
- `process.py`: Server-side script for uploading vector matrices.
- `query.py`: Client-side script for querying hot topics within a specified time period; results are stored in `picture` and `result_excel` directories.
- `README.md`: Contains the project description and instructions.
- `requirements.txt`: Lists all the Python dependencies required for the project.
- Other scripts and resources are part of the project's supporting files.

### Training the Sentiment Analysis Model with TensorFlow

1. To train the sentiment analysis model using TensorFlow:
    ```bash
    jupyter notebook add_new_mind.ipynb
    ```
   Follow the instructions in the notebook to train and evaluate the model.

### Training with MXNet (Optional)

1. If you wish to experiment with the MXNet model, run:
    ```bash
    python mxnet_code.py
    ```
   However, for this project, the TensorFlow model provided better results and will be used for further processing.

### Uploading Vector Matrices

1. Execute the `process.py` script on the server to upload vector matrices:
    ```bash
    python process.py
    ```
   Ensure the server environment is correctly configured as described in the installation guide.

### Querying Hot Topics and Generating Results

1. Run the `query.py` script to query hot topics and generate visualizations:
    ```bash
    python query.py
    ```
   The outputs will be saved in the `picture` directory as visualizations and `result_excel` as spreadsheets.

Remember to install all required Python dependencies listed in `requirements.txt` before running the scripts. Use the following command to install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

Ensure that the appropriate fonts are installed if you encounter issues with missing fonts during visualization generation, as previously described in the installation guide.

