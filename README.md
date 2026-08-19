# AWS-Services-Cost-Minimization
Minimize cost usage of my EC2 machines using Lambda and EvenBridge


# 🕒 AWS Automated EC2 Shutdown Scheduler

An automated, serverless, and **100% cost-free** solution to automatically shut down all running AWS EC2 instances daily at **12:00 PM (noon)**. This project leverages **AWS Lambda** (Python) and **Amazon EventBridge** to optimize cloud spending by eliminating idle infrastructure costs.

---

## 🏗️ Architecture Overview

The architecture follows a fully serverless event-driven pattern:
1. **Amazon EventBridge Schedule** triggers a CRON event every day at 12:00 PM.
2. **AWS Lambda** invokes a Python script using `boto3` to scan all EC2 instances across the region.
3. **AWS IAM Role** grants the Lambda function explicit permissions to list and stop EC2 instances.
4. **Amazon CloudWatch Logs** records the execution history for audit tracking.

---

## 🛠️ Step-by-Step Implementation

### Step 1: Create the IAM Policy & Role
Lambda needs specific security permissions to interact with your EC2 instances.

1. Open the **AWS IAM Console**.
2. Go to **Policies** > **Create policy** > Switch to the **JSON** tab.
3. Paste the following policy definition:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:StopInstances"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```
4. Click **Next**, name it `LambdaEC2StopPolicy`, and click **Create policy**.
5. Go to **Roles** > **Create role** > Select **AWS Service** > **Lambda**.
6. Attach the `LambdaEC2StopPolicy` you just created.
7. Name the role `LambdaEC2StopRole` and finalize creation.

---

### Step 2: Deploy the AWS Lambda Function
This script automatically discovers all running instances and triggers a graceful shutdown.

1. Open the **AWS Lambda Console** and click **Create function**.
2. Choose **Author from scratch** with the following parameters:
   * **Function name:** `StopAllEC2Instances`
   * **Runtime:** `Python 3.12` (or latest)
3. Under **Change default execution role**, select **Use an existing role** and choose `LambdaEC2StopRole`.
4. Click **Create function**.
5. In the **Code** tab, replace the default blueprint with this script:

```python
import boto3
import logging

# Set up logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # Retrieve all EC2 instances that are currently running
    filters = [{'Name': 'instance-state-name', 'Values': ['running']}]
    
    response = ec2.describe_instances(Filters=filters)
    instances_to_stop = []
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances_to_stop.append(instance['InstanceId'])
            
    # Check if there are any running instances to stop
    if not instances_to_stop:
        logger.info("No running EC2 instances found to stop.")
        return {
            'statusCode': 200,
            'body': "No running instances found."
        }
        
    # Stop the running instances
    logger.info(f"Attempting to stop the following EC2 instances: {instances_to_stop}")
    ec2.stop_instances(InstanceIds=instances_to_stop)
    logger.info("Successfully issued stop command to all running instances.")
    
    return {
        'statusCode': 200,
        'body': f"Successfully stopped instances: {instances_to_stop}"
    }
```
6. Click **Deploy** to save and commit your code changes.

---

### Step 3: Schedule the Trigger with Amazon EventBridge
This rule acts as an automated alarm clock to execute your function at noon.

1. Open the **Amazon EventBridge Console**.
2. Navigate to **Schedules** (or **Rules**) and click **Create schedule**.
3. Configure the schedule pattern:
   * **Schedule pattern:** Recurring schedule -> **Cron-based schedule**
   * **Cron expression:** `0 12 * * ? *` (Fires at 12:00 PM daily)
   * **Time zone:** Select your local or target project time zone.
4. Click **Next** and select **AWS Lambda** as your target.
5. Choose your `StopAllEC2Instances` function from the dropdown.
6. Leave optional settings as default and click **Create schedule**.

---

## 💰 Cost Analysis & Financial Impact

This automation configuration utilizes the permanent **AWS Free Tier** structures, guaranteeing a total operational cost of **$0.00**.

| AWS Component | Free Tier Allowance (Monthly) | Project Consumption (Monthly) | Total Estimated Cost |
| :--- | :--- | :--- | :--- |
| **AWS Lambda** | 1,000,000 Free Requests | ~30 Requests | **$0.00** |
| **Amazon EventBridge** | 14,000,000 Free Invocations | ~30 Invocations | **$0.00** |
| **CloudWatch Logs** | 5 GB Free Storage | < 1 MB | **$0.00** |

> ⚠️ **Note:** While this script costs nothing to run, keep in mind that stopping an EC2 instance stops compute billing instantly, but underlying **EBS storage volumes** and unattached **Elastic IPs** will still incur regular AWS storage fees.

---

## 🧪 Testing the Pipeline
To ensure everything functions correctly without waiting until 12:00 PM:
1. Open your `StopAllEC2Instances` function in the Lambda Console.
2. Click on the **Test** tab.
3. Keep the default empty JSON template, give it a name (e.g., `TestExecution`), and click **Save**.
4. Spin up a temporary EC2 instance, wait for it to be `Running`, then hit **Test** in Lambda.
5. Verify that your EC2 instance switches status to `Stopping` / `Stopped`.
