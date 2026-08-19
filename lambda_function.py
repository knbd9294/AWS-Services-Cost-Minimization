import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # 1. Récupérer toutes les instances en cours d'exécution (Running)
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    instance_ids = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
            
    # 2. Arrêter les instances si certaines sont actives
    if instance_ids:
        print(f"Arrêt des instances suivantes : {instance_ids}")
        ec2.stop_instances(InstanceIds=instance_ids)
        return {
            'statusCode': 200,
            'body': f"Successfully requested stop for instances: {instance_ids}"
        }
    else:
        print("Aucune instance en cours d'exécution trouvée.")
        return {
            'statusCode': 200,
            'body': "No running instances to stop."
        }
