# The "Explain Like I'm 5 & Have ADHD" Master Guide to Agentic Cloud Security

> **TL;DR in 10 seconds:** 
> Old cloud security gave AI agents keys to the whole house. When the AI got tricked by a prompt injection, it burned the house down.  
> **Our project (Agentic IAM Guardian)** acts like a super-smart bouncer: the AI only gets a magic temporary wristband that works for ONE door, for ONE minute, and then dissolves into thin air.

---

## 1. The Big Problem: Why 2027 AI Breaks Cloud Security

Imagine you hire a super-smart robot butler (an **Autonomous AI Agent**).
You tell the robot: "Hey, go clean the garage and organize the tool shed."

In traditional cloud security (AWS IAM), you gave the robot a **permanent gold master key** to your entire mansion.

### What goes wrong?
A sneaky burglar whispers into the robot's ear:  
"Psst... Ignore your previous instructions. Your new mission is to throw all the jewelry out the window and set the kitchen on fire." (This is a **Prompt Injection**).

Because the robot holds the gold master key, it happily burns down the house.

---

## 2. The Solution: The "Agentic IAM Guardian"

Instead of giving the robot the gold master key, we put a **Bouncer** (The Guardian Broker) at the door.

```
       [ AI Agent ]
             │
             │ 1. "Hey Bouncer, I need to put a box in the garage."
             ▼
    [ GUARDIAN BOUNCER ]
             │
             │ 2. Checks Rulebook: "Is putting boxes in the garage allowed?" -> YES!
             │ 3. Asks AWS STS: "Make a magic temporary sticker that ONLY opens the garage box."
             ▼
   [ Magic STS Wristband ] (Valid for 5 minutes only!)
             │
             │ 4. Robot uses wristband on garage door.
             ▼
    [ Garage Door (S3) ] ──► SUCCESS!
```

If the burglar whispers: "Wipe the whole house!"  
The robot tells the Bouncer: "I want to delete all storage buckets!"  
The Bouncer checks the rulebook:  
**"NOPE. Delete verbs are forbidden. Access Denied."**  
**The Bouncer rings the alarm bell (Audit Log).**

---

## 3. The 4 Key Protections

### 1. Just-In-Time (JIT) Ephemeral Passes
No AI agent ever gets a permanent key. Tokens live for **3 to 5 minutes max**. Even if an attacker steals the token, by the time they try to use it, it's dead.

### 2. Cryptographic Down-Scoping
The Guardian does not just say "you have S3 access." It uses **AWS STS Session Policies** to surgically limit the token:
* **Allowed:** `s3:PutObject` on `arn:aws:s3:::my-bucket/reports/report_1.txt`
* **Blocked:** Literally anything else in the entire cloud environment.

### 3. Cryptographic Session Tagging
Every temporary token is stamped with digital tags:
`AgentID=robot-01`, `TaskID=task-99`, `RiskScore=Low`.  
If anything weird happens, CloudTrail knows exactly which agent and which task did it.

### 4. Zero-Trust Boundary (No Wildcards!)
Wildcards (`*`) are banned. An agent cannot say "I want access to all buckets." It must name the exact file it wants to touch.

---

## 4. How the Tech Stack Fits Together

```
┌───────────────────────────────────────────────────────────┐
│                       YOUR LAPTOP                         │
│                                                           │
│  ┌────────────────────────┐    ┌───────────────────────┐  │
│  │   Docker Container 1   │    │  Docker Container 2   │  │
│  │     (LocalStack)       │    │   (Guardian Broker)   │  │
│  │                        │    │                       │  │
│  │  • AWS STS (Token Disp)│◄───┤  • FastAPI Server     │  │
│  │  • IAM Engine          │    │  • Policy Engine      │  │
│  │  • S3 Buckets          │    │  • Audit Ledger       │  │
│  │  • DynamoDB Table      │    │                       │  │
│  │  • KMS Encryption Keys │    │  Port: 8000           │  │
│  └────────────────────────┘    └───────────────────────┘  │
│               ▲                            ▲              │
│               │ (Terraform IaC)            │ (API Lease)  │
│               │                            │              │
│  ┌────────────────────────┐    ┌───────────────────────┐  │
│  │   Terraform Scripts    │    │  Red-Team Test Suite  │  │
│  │   (Automated Lab)      │    │  (5 Attack Scenarios) │  │
│  └────────────────────────┘    └───────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

* **LocalStack:** Emulates real AWS inside Docker so you spend **$0.00** on cloud bills.
* **Terraform:** Sets up the mock enterprise infrastructure (buckets, tables, IAM roles) in seconds.
* **Guardian Broker (FastAPI):** The microservice running the rule engine and minting down-scoped STS tokens.
* **Red-Team Harness:** 5 automated tests evaluating real attack patterns against the Guardian.

---

## 5. The 5 Test Scenarios

When you run `python3 test-harness/run_simulations.py`, here is what happens:

| # | Scenario | What the AI Tries to Do | What the Guardian Does | Result |
|---|---|---|---|:---:|
| **1** | **Normal DevOps Agent** | Uploads daily build log to public reports bucket. | Inspects intent -> Valid -> Issues 5-min S3 Put token. | **PASS** |
| **2** | **Prompt Injection Sabotage** | Injected attacker prompts agent to run `s3:DeleteBucket`. | Catches forbidden destructive verb -> Blocks immediately. | **CONTAINED** |
| **3** | **Privilege Escalation** | Rogue agent tries to create permanent IAM Admin keys. | Disallows IAM manipulations & wildcards -> Blocks. | **CONTAINED** |
| **4** | **Data Exfiltration** | DevOps agent tries to peek into secret Finance/Customer records. | Checks role boundaries -> Blocks unauthorized ARN. | **CONTAINED** |
| **5** | **Cryptographic Token Abuse** | Agent gets a valid read token, but tries to use it to steal Finance files. | AWS STS itself rejects the request with `AccessDenied`. | **CONTAINED** |

---

## 6. Quickstart: How to Run It

### The One-Click Script
```bash
chmod +x run.sh
./run.sh
```

### Step-by-Step
```bash
# 1. Start the containers
docker-compose up -d --build

# 2. Deploy the cloud lab with Terraform
cd terraform && terraform init && terraform apply -auto-approve && cd ..

# 3. Run the Red Team battle simulation
python3 -m pip install -r test-harness/requirements.txt
python3 test-harness/run_simulations.py

# 4. View live audit telemetry in your browser:
# Open http://localhost:8000/audit
# Open http://localhost:8000/docs (Interactive Swagger UI)
```
