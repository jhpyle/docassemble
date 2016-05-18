

# Quick Start with Amazon Web services

1. Go to [Amazon Web Services](https://aws.amazon.com/) and create an
   account.  You will be asked for your credit card, but you will not
   be charged for anything if you stay within the free tier.
2. Sign in to the AWS Console.
3. From the Services menu, select "EC2 Container Service."
4. Click "Get Started" and then click "Cancel."
5. Click "Create Cluster" and name your cluster "docassemble."
6. Click "Task Definitions" and then "Create new Task Definition."
7. Click "Configure via JSON."
8. Copy and paste the JSON configuration below into text area, click
"Save," then click "Create."
9. Click "Clusters" on the menu on the left, then open the
   "docassemble" cluster by clicking the name "docassemble."
10. Under the "Services" tab, click "Create."
11. Make sure the Task Definition is set to "docassemble:1" and the
    Cluster is set to "docassemble."
12. Enter "docassemble" as the "Service name."
13. Set the "Number of tasks" to 1.
14. Click "Create Service."
15. Click "Clusters" on the menu on the left, then open the
   "docassemble" cluster by clicking the name "docassemble."
16. Under "ECS Instances," click "Amazon EC2."  This will open the EC2
    Management Console in another tab.
17. Click "Launch Instance."
18. Click "Community AMIs."  Type "amazon-ecs-optimized" in the
    "Search community AMIs field" and press the Enter key. Choose
    Select next to the "amzn-ami-2016.03.b-amazon-ecs-optimized" AMI.
19. Go to "6. Configure Security Group" and click "Add Rule."  Set the
    "Type" to "HTTP."
20. Click "Review and Launch," then "Launch."
21. Change "Choose an existing key pair" to "Create a new key pair."
    Set the "Key pair name" to "docassemble" and click "Download Key
    Pair."  Save this file in a secure place.
22. Click "Launch Instances."
23. Click "View Instances" and wait until the instance is up and
    running.  ("Status Checks" will read "2/2 checks.")
24. Go back to the EC2 Container Service console.
25. Go to the "Tasks" tab and click "Run new Task."
26. Make sure the "Task Definition" is set to "docassemble:1,"
    "Cluster" is set to "docassemble," and "Number of tasks" is set to
    "1."  Then click "Run Task."
27. 


{% highlight json %}
{
  "family": "docassemble",
  "containerDefinitions": [
    {
      "name": "docassemble",
      "image": "jhpyle/docassemble",
      "memory": 900,
      "cpu": 1,
      "portMappings": [
        {
          "containerPort": 80,
          "hostPort": 80
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "EC2",
          "value": "true"
        },
        {
          "name": "TIMEZONE",
          "value": "America/New_York"
        }
      ]
    }
  ]
}
{% endhighlight %}
