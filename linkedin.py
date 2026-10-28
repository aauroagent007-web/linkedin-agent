import openai
import requests
import os
import textwrap
import json
import hashlib
import base64
import math
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io

# ReportLab imports for PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable
)
from reportlab.platypus import Image as RLImage
from reportlab.lib.colors import HexColor
from PIL import Image as PILImage

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
LINKEDIN_ACCESS_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_PERSON_ID = os.environ["LINKEDIN_PERSON_ID"]
TOPIC = os.environ.get("TOPIC", "Agentic AI cybersecurity and autonomous threat detection")
RUN_MODE = os.environ.get("RUN_MODE", "post")

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

LINKEDIN_HEADERS = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

PROFILE_IMAGE_URL = (
    "https://media.licdn.com/dms/image/v2/C4D03AQHnswiAnQJbMg/"
    "profile-displayphoto-shrink_800_800/"
    "profile-displayphoto-shrink_800_800/0/1516492188066"
    "?e=1781136000&v=beta&t=fSaDr16J6btRG0W3a32V__c-slLPrTscWAGJGI6vxEE"
)

DAILY_TOPICS = [
    # 1. Advanced AI and Superintelligence Research
    "Artificial Superintelligence (ASI): Research Frontiers and Architectures",
    "ASI-Oriented Intelligence: Adaptive Reasoning, Memory, and Self-Evaluation",
    "Artificial General Intelligence (AGI) vs ASI: Capabilities and Limitations",
    "Recursive Self-Improvement in AI: Safety, Evaluation, and Control",
    "AI Cognitive Architectures for Long-Horizon Planning",
    "Predictive Intelligence Systems Using Advanced AI",
    "World Models and Model-Based Reasoning for Autonomous AI",
    "Neuro-Symbolic AI for Advanced Reasoning and Decision-Making",
    "Metacognition and Self-Reflection in AI Systems",
    "Continual Learning and Adaptive Intelligence Architectures",

    # 2. AI Swarms and Multi-Agent Intelligence
    "AI Swarm Intelligence: Distributed Reasoning and Collective Intelligence",
    "Multi-Agent AI Systems: Architectures, Coordination, and Communication",
    "Hierarchical AI Agent Swarms and Dynamic Task Allocation",
    "Emergent Behavior in Multi-Agent AI Systems",
    "Swarm Intelligence for Autonomous Cyber Defense",
    "Agent-to-Agent Communication Protocols and Security",
    "Multi-Agent Reinforcement Learning for Collaborative Intelligence",
    "Decentralized AI Swarms and Distributed Decision-Making",
    "Consensus Mechanisms for Autonomous AI Agents",
    "Swarm Intelligence for Predictive Threat Detection",
    "Self-Organizing AI Agents and Adaptive Coordination",
    "Heterogeneous AI Agent Teams for Complex Problem Solving",
    "Agent Orchestration Using Graph-Based Workflows",
    "Collective Memory and Knowledge Sharing Across AI Agents",
    "Multi-Agent Evaluation, Benchmarking, and Failure Analysis",

    # 3. Agentic AI and Autonomous Systems
    "Agentic AI Architectures for Autonomous Research",
    "Autonomous AI Planning and Goal Decomposition",
    "Tool-Using AI Agents and Secure Function Calling",
    "Long-Horizon Autonomous Agents with Persistent Memory",
    "AI Agent Self-Evaluation and Reflection Loops",
    "Agentic Workflow Optimization and Dynamic Routing",
    "Human-in-the-Loop Control for Autonomous AI",
    "AI Agents with Retrieval-Augmented Generation (RAG)",
    "Multi-Agent Systems Using CrewAI, LangGraph, and AutoGen",
    "Autonomous AI Research Agents and Evidence Verification",
    "Agentic AI Reliability and Task Completion Evaluation",
    "AI Agent Memory Architectures and Knowledge Graphs",
    "Model Context Protocol (MCP) Security for AI Agents",
    "Interoperability Standards for Multi-Agent AI Systems",
    "Autonomous AI Agents: Planning, Execution, and Governance",

    # 4. AI Security and Adversarial Research
    "Prompt Injection Attacks on AI Agents",
    "Indirect Prompt Injection and Untrusted Data Boundaries",
    "Zero Trust Architecture for AI Systems",
    "LLM Security and Jailbreaking Prevention",
    "AI Supply Chain Security Risks",
    "Multi-Agent System Vulnerabilities",
    "Adversarial Machine Learning Attacks",
    "AI Model Poisoning and Data Integrity Protection",
    "AI Agent Authentication and Authorization Frameworks",
    "AI Agent Identity Management and Credential Security",
    "AI Agent Sandboxing and Least-Privilege Execution",
    "Tool-Call Abuse and Excessive Agency in AI Systems",
    "AI Memory Poisoning and Persistent Context Attacks",
    "RAG Pipeline Security and Vector Database Attacks",
    "Model Theft, Extraction, and Intellectual Property Protection",
    "AI Inference Endpoint Security and Rate Limiting",
    "LLM Denial-of-Service and Resource Exhaustion Attacks",
    "Multimodal AI Security: Image, Audio, and Video Attacks",
    "AI Safety Guardrails and Policy Enforcement",
    "Secure AI Model Deployment and Runtime Protection",

    # 5. AI-Powered Cybersecurity and Autonomous Defense
    "Autonomous Threat Hunting with AI",
    "Agentic AI in Security Operations Centers (SOC)",
    "AI-Powered Malware Detection and Classification",
    "Autonomous Incident Response Systems",
    "AI Red Teaming and Adversarial Security Evaluation",
    "AI-Driven Vulnerability Assessment and Prioritization",
    "AI-Assisted Secure Code Review and SAST",
    "AI-Powered Software Composition Analysis",
    "AI Security Testing for APIs and Microservices",
    "Autonomous Attack Surface Management",
    "AI-Powered External Threat Intelligence",
    "AI-Assisted Digital Forensics and Incident Investigation",
    "AI-Driven Detection Engineering and SIEM Rule Generation",
    "AI-Powered Endpoint Detection and Response (EDR)",
    "Predictive Cyber Threat Intelligence and Early Warning",
    "AI-Assisted Threat Modeling with MITRE ATT&CK",
    "Autonomous Security Validation and Continuous Control Testing",
    "AI-Based Vulnerability Exploitability Prediction",
    "AI-Assisted Cloud Security Posture Management",
    "Autonomous Security Configuration and Compliance Validation",

    # 6. Predictive Intelligence and Threat Analytics
    "Predictive Cybersecurity Using Machine Learning and AI",
    "Graph Neural Networks for Threat Intelligence",
    "Knowledge Graphs for Cyber Threat Correlation",
    "Temporal Graph Learning for Attack Prediction",
    "Bayesian Reasoning for Cyber Risk Prediction",
    "Causal AI for Root-Cause Analysis of Security Incidents",
    "Explainable AI for Security Alert Prioritization",
    "Behavioral Analytics Using Multi-Agent AI",
    "Anomaly Detection in Network and Endpoint Telemetry",
    "Federated Threat Intelligence and Privacy-Preserving Learning",
    "AI-Based Insider Threat Detection",
    "Cross-Domain Security Event Correlation",
    "Cyber Attack Path Prediction Using AI",
    "Uncertainty Quantification in AI-Based Threat Detection",
    "AI-Based Risk Scoring and Adaptive Security Prioritization",

    # 7. AI Governance, Trust, and Safety
    "AI Governance Frameworks for Autonomous Systems",
    "AI Alignment and Control for Increasingly Capable Systems",
    "Scalable Oversight of Advanced AI Systems",
    "AI Interpretability and Mechanistic Interpretability Research",
    "AI Agent Accountability and Decision Traceability",
    "AI Risk Management Using NIST AI RMF",
    "ISO/IEC 42001 AI Management System Security",
    "AI Red Teaming and Safety Benchmark Development",
    "AI Sandboxing and Containment for High-Capability Models",
    "Runtime Monitoring and Policy Enforcement for AI Agents",
    "AI Evaluation Against Deception and Reward Hacking",
    "Human Oversight of Autonomous Cybersecurity Decisions",
    "AI Audit Trails, Provenance, and Evidence-Based Reporting",
    "Responsible Disclosure of AI Vulnerabilities",
    "AI Security Assurance and Continuous Risk Assessment",

    # 8. Advanced Machine Learning Research
    "Transformer Architecture Optimization and Efficient Attention",
    "Mixture-of-Experts Models and Sparse Intelligence",
    "Small Language Models for On-Premises Cybersecurity",
    "Multimodal Foundation Models for Security Analytics",
    "Reinforcement Learning for Tool-Using AI Agents",
    "Synthetic Data Generation for Security Model Training",
    "Self-Supervised Learning for Unknown Threat Detection",
    "Continual Learning Under Adversarial Distribution Shifts",
    "Parameter-Efficient Fine-Tuning for Cybersecurity Models",
    "Retrieval-Augmented Generation Versus Fine-Tuning",
    "Model Quantization and Efficient AI Inference",
    "AI Benchmark Contamination and Evaluation Integrity",
    "Reasoning Models: Reliability, Verification, and Limitations",
    "Causal Representation Learning for Cybersecurity",
    "Neural-Symbolic Systems for Verifiable AI Decisions",

    # 9. Emerging and Experimental Technologies
    "Quantum Machine Learning for Cybersecurity Research",
    "Post-Quantum Cryptography and AI Security",
    "AI for Space Cybersecurity and Satellite Threat Detection",
    "AI-Driven RF Signal Analysis and Spectrum Anomaly Detection",
    "Privacy-Preserving AI Using Secure Enclaves",
    "Homomorphic Encryption for Confidential AI Inference",
    "Decentralized AI Networks and Federated Agent Systems",
    "Digital Twins for Cybersecurity Simulation",
    "AI-Based Robotics and Autonomous System Security",
    "Neuromorphic Computing for Energy-Efficient Intelligence",
    "AI for OT and Industrial Control System Security",
    "AI Security for Edge Computing and IoT Devices",
    "Synthetic Media Detection and Deepfake Forensics",
    "AI-Assisted Software Supply Chain Risk Analysis",
    "AI Research on Autonomous Scientific Discovery",

    # 10. Practical Research, Experiments, and Benchmarks
    "Open-Source Agentic AI Security Frameworks",
    "Benchmarking Multi-Agent Swarm Coordination",
    "Evaluating AI Agent Reliability Under Adversarial Conditions",
    "Building a Secure Multi-Agent Cybersecurity Research Lab",
    "Comparing Single-Agent, Multi-Agent, and Swarm Architectures",
    "Testing AI Agent Isolation in Docker Containers",
    "Evaluating AI Agents Against OWASP Top 10 for LLM Applications",
    "Designing Reproducible AI Security Experiments",
    "Measuring Swarm Intelligence Efficiency and Coordination Costs",
    "Evaluating Predictive Threat Detection Accuracy",
    "AI Cybersecurity Research Using OpenCTI and MITRE ATT&CK",
    "Building an AI-Assisted SOC with Wazuh and OpenCTI",
    "Secure Automation of CodeQL and SAST Analysis",
    "AI-Assisted API Security Testing in Authorized Environments",
    "Developing a Cybersecurity and AI Trust Engine",
]

HASHTAG_SETS = {
    # 1. ASI, AGI and Advanced Intelligence
    "ASI Research": (
        "#ASI #ArtificialSuperintelligence #AGI #AdvancedAI "
        "#AIResearch #CognitiveArchitecture #MachineIntelligence "
        "#AdaptiveIntelligence #AISafety #AIAlignment "
        "#ReasoningModels #FutureOfAI #NeuralNetworks "
        "#AIInnovation #IntelligentSystems"
    ),

    "AGI Research": (
        "#AGI #ArtificialGeneralIntelligence #GeneralAI "
        "#AIResearch #MachineLearning #DeepLearning "
        "#CognitiveAI #AIReasoning #WorldModels "
        "#ContinualLearning #AIArchitecture #AISafety "
        "#IntelligentAgents #FutureOfAI #NeuroSymbolicAI"
    ),

    "Self-Improving AI": (
        "#SelfImprovingAI #RecursiveSelfImprovement "
        "#AISafety #AIAlignment #ASI #AGI "
        "#AIResearch #AdaptiveAI #MetaLearning "
        "#AIReasoning #ModelEvaluation #ResponsibleAI "
        "#AIControl #MachineIntelligence #AdvancedAI"
    ),

    # 2. AI Swarms and Multi-Agent Intelligence
    "AI Swarm Intelligence": (
        "#AISwarm #SwarmIntelligence #SwarmAI "
        "#MultiAgentSystems #MultiAgentAI #AgenticAI "
        "#CollectiveIntelligence #DistributedAI "
        "#AutonomousAgents #AIResearch #AIAgents "
        "#CollaborativeAI #EmergentBehavior "
        "#DecentralizedAI #IntelligentSystems"
    ),

    "Multi-Agent Systems": (
        "#MultiAgentSystems #MultiAgentAI #AIAgents "
        "#AgenticAI #AgentOrchestration #SwarmAI "
        "#DistributedIntelligence #AgentCoordination "
        "#MultiAgentLearning #CrewAI #LangGraph "
        "#AutonomousAgents #AIResearch #LLMOps #AISecurity"
    ),

    "Swarm Cybersecurity": (
        "#AISwarm #SwarmIntelligence #Cybersecurity "
        "#AutonomousCyberDefense #AgenticAI #AISecurity "
        "#ThreatHunting #ThreatIntelligence #MultiAgentAI "
        "#SOC #BlueTeam #CyberDefense #AIAgents "
        "#PredictiveSecurity #SecurityAutomation"
    ),

    "Multi-Agent Security": (
        "#MultiAgentSecurity #MultiAgentSystems #AISecurity "
        "#AgenticAI #AIAgents #LLMSecurity "
        "#AgentSecurity #PromptInjection #ZeroTrust "
        "#AIThreatModeling #SecureAI #Cybersecurity "
        "#AIResearch #RuntimeSecurity #AITrust"
    ),

    # 3. Agentic AI and Autonomous Research
    "Agentic AI": (
        "#AgenticAI #AIAgents #AutonomousAgents "
        "#AIResearch #LLMOps #AIWorkflows "
        "#AgentOrchestration #MultiAgentSystems "
        "#ToolCalling #RAG #AIEngineering "
        "#MachineLearning #IntelligentAutomation "
        "#AIInnovation #AISecurity"
    ),

    "Autonomous AI Research": (
        "#AutonomousResearch #ResearchAgents #AgenticAI "
        "#AIAgents #AIResearch #MultiAgentAI "
        "#ScientificDiscovery #AIReasoning "
        "#KnowledgeGraphs #RAG #LLMOps "
        "#AutomatedResearch #AIEngineering "
        "#IntelligentSystems #FutureOfAI"
    ),

    "AI Memory and Reasoning": (
        "#AIMemory #AIReasoning #AgenticAI "
        "#LongTermMemory #CognitiveArchitecture "
        "#KnowledgeGraphs #RAG #LLMResearch "
        "#Metacognition #WorldModels #AIPlanning "
        "#ContinualLearning #MultiAgentAI "
        "#AIResearch #AdvancedAI"
    ),

    # 4. AI Security and Adversarial Research
    "Prompt Injection": (
        "#PromptInjection #IndirectPromptInjection "
        "#AIAgents #LLMSecurity #AgenticAI "
        "#Cybersecurity #AISecurity #AIAttacks "
        "#PromptHacking #ZeroTrust #AIThreatModeling "
        "#AIResearch #ThreatDetection #DevSecOps "
        "#ResponsibleAI"
    ),

    "Zero Trust": (
        "#ZeroTrust #ZeroTrustSecurity #IAM "
        "#IdentitySecurity #AgenticAI #Cybersecurity "
        "#CloudSecurity #NetworkSecurity #AISecurity "
        "#DevSecOps #MLOps #ZeroTrustArchitecture "
        "#AIResearch #SecurityArchitecture #LeastPrivilege"
    ),

    "LLM Security": (
        "#LLMSecurity #LLM #GenAI #AISecurity "
        "#Jailbreaking #PromptInjection #RAGSecurity "
        "#AIThreats #AITrust #SecureAI "
        "#AIRedTeaming #OWASP #Cybersecurity "
        "#AIResearch #ResponsibleAI"
    ),

    "AI Supply Chain": (
        "#AISupplyChain #AIModelSecurity #MLOpsSecurity "
        "#SoftwareSupplyChain #ModelPoisoning "
        "#DataSecurity #AISecurity #DevSecOps "
        "#MLSecurity #ModelIntegrity #Cybersecurity "
        "#AIResearch #SecureMLOps #CloudSecurity "
        "#RiskManagement"
    ),

    "Adversarial Machine Learning": (
        "#AdversarialML #MachineLearningSecurity "
        "#AdversarialAI #ModelPoisoning #AISecurity "
        "#AIResearch #DeepLearning #ModelRobustness "
        "#DataIntegrity #AIThreats #MLSecurity "
        "#SecureAI #ResponsibleAI #Cybersecurity "
        "#RobustAI"
    ),

    "AI Red Teaming": (
        "#AIRedTeaming #LLMSecurity #AISecurity "
        "#AgenticAI #AIAgents #PromptInjection "
        "#AdversarialAI #AIThreatModeling "
        "#OWASP #MITREATTACK #Cybersecurity "
        "#AIResearch #SecurityTesting "
        "#ResponsibleAI #AITrust"
    ),

    "AI Agent Security": (
        "#AIAgentSecurity #AgenticAI #AISecurity "
        "#AgentIdentity #LeastPrivilege #ZeroTrust "
        "#SecureAI #ToolSecurity #Sandboxing "
        "#PromptInjection #MultiAgentSystems "
        "#RuntimeSecurity #LLMSecurity "
        "#Cybersecurity #AITrust"
    ),

    # 5. Autonomous Cyber Defense and SOC
    "Autonomous Cyber Defense": (
        "#AutonomousCyberDefense #AgenticAI "
        "#AISecurity #Cybersecurity #AIAgents "
        "#ThreatHunting #ThreatIntelligence "
        "#SecurityAutomation #SOC #SIEM "
        "#IncidentResponse #BlueTeam "
        "#PredictiveSecurity #CyberDefense "
        "#AIResearch"
    ),

    "AI SOC Operations": (
        "#AISOC #SOC #AgenticAI #AIOps "
        "#Cybersecurity #SecurityOperations "
        "#SIEM #SOAR #Wazuh #ThreatHunting "
        "#IncidentResponse #ThreatIntelligence "
        "#SecurityAutomation #AISecurity #AIResearch"
    ),

    "AI Threat Intelligence": (
        "#ThreatIntelligence #CyberThreatIntelligence "
        "#AIThreatIntelligence #AgenticAI "
        "#AISecurity #OpenCTI #MITREATTACK "
        "#ThreatHunting #PredictiveAnalytics "
        "#Cybersecurity #OSINT #SOC "
        "#ThreatDetection #AIResearch "
        "#ExternalThreatIntelligence"
    ),

    "AI Vulnerability Assessment": (
        "#AIVulnerabilityAssessment #VAPT #AppSec "
        "#Cybersecurity #AISecurity #AgenticAI "
        "#DAST #SAST #CodeQL #OWASP "
        "#APISecurity #DevSecOps #SecureCoding "
        "#VulnerabilityManagement #AIResearch"
    ),

    "AI Incident Response": (
        "#IncidentResponse #AutonomousResponse "
        "#AgenticAI #AISecurity #SOC #SOAR "
        "#ThreatHunting #DigitalForensics "
        "#CyberDefense #SecurityAutomation "
        "#ThreatIntelligence #Wazuh "
        "#Cybersecurity #AIResearch #BlueTeam"
    ),

    # 6. Predictive Intelligence and Threat Analytics
    "Predictive Intelligence": (
        "#PredictiveIntelligence #PredictiveAI "
        "#ThreatPrediction #CyberThreatIntelligence "
        "#MachineLearning #GraphNeuralNetworks "
        "#KnowledgeGraphs #CausalAI #AgenticAI "
        "#Cybersecurity #AnomalyDetection "
        "#ThreatAnalytics #AIResearch "
        "#RiskPrediction #AISecurity"
    ),

    "AI Threat Detection": (
        "#ThreatDetection #AIThreatDetection "
        "#AnomalyDetection #MachineLearning "
        "#DeepLearning #Cybersecurity #AISecurity "
        "#ThreatHunting #SIEM #SOC "
        "#PredictiveSecurity #BehavioralAnalytics "
        "#ThreatIntelligence #AIResearch #EDR"
    ),

    "Graph AI and Cybersecurity": (
        "#GraphAI #GraphNeuralNetworks #KnowledgeGraphs "
        "#Cybersecurity #ThreatIntelligence "
        "#AttackGraph #ThreatDetection #CausalAI "
        "#PredictiveAnalytics #MachineLearning "
        "#AgenticAI #AISecurity #AIResearch "
        "#AttackPathAnalysis #DataScience"
    ),

    # 7. AI Trust, Safety, Governance and Alignment
    "AI Trust and Safety": (
        "#AITrust #AISafety #AIAlignment "
        "#ResponsibleAI #AIControl #AIGovernance "
        "#AITransparency #AIAccountability "
        "#AIResearch #AgenticAI #AISecurity "
        "#HumanInTheLoop #TrustworthyAI "
        "#RiskManagement #FutureOfAI"
    ),

    "AI Governance": (
        "#AIGovernance #ResponsibleAI #AISafety "
        "#AICompliance #ISO42001 #NISTAIRMF "
        "#AITrust #AIAccountability #AITransparency "
        "#Cybersecurity #AIResearch #RiskManagement "
        "#AIRegulation #SecureAI #DataGovernance"
    ),

    "AI Alignment and Control": (
        "#AIAlignment #AIControl #AISafety "
        "#ScalableOversight #AdvancedAI #ASI "
        "#AGI #ResponsibleAI #AIResearch "
        "#MechanisticInterpretability #AITrust "
        "#HumanOversight #ModelEvaluation "
        "#AIAlignmentResearch #TrustworthyAI"
    ),

    "Explainable AI": (
        "#ExplainableAI #XAI #ResponsibleAI "
        "#AITransparency #InterpretableAI "
        "#MachineLearning #AISafety #AITrust "
        "#Cybersecurity #ThreatDetection "
        "#AIResearch #ModelExplainability "
        "#TrustworthyAI #DataScience #AI Ethics"
    ).replace("#AI Ethics", "#AIEthics"),

    # 8. Advanced Machine Learning Research
    "Advanced AI Research": (
        "#AIResearch #DeepLearning #MachineLearning "
        "#FoundationModels #ReasoningModels "
        "#NeuroSymbolicAI #WorldModels #MixtureOfExperts "
        "#ContinualLearning #MultimodalAI "
        "#AIInnovation #AdvancedAI #AGI "
        "#IntelligentSystems #FutureOfAI"
    ),

    "Generative AI Security": (
        "#GenerativeAI #GenAI #LLMSecurity "
        "#AIGeneratedContent #AISecurity "
        "#PromptInjection #AIThreats #RAGSecurity "
        "#AITrust #ResponsibleAI #Cybersecurity "
        "#AIResearch #ModelSecurity "
        "#FoundationModels #AIEngineering"
    ),

    "Reinforcement Learning": (
        "#ReinforcementLearning #MultiAgentRL "
        "#RL #MachineLearning #DeepLearning "
        "#AIResearch #SwarmIntelligence "
        "#AgenticAI #AutonomousAgents "
        "#DecisionMaking #AdaptiveAI "
        "#AIReasoning #AdvancedAI "
        "#IntelligentSystems #AIInnovation"
    ),

    # 9. Emerging and Experimental Technologies
    "Quantum AI": (
        "#QuantumAI #QuantumComputing "
        "#QuantumMachineLearning #PostQuantumCryptography "
        "#Cybersecurity #AISecurity #AIResearch "
        "#QuantumSecurity #MachineLearning "
        "#AdvancedComputing #Cryptography "
        "#FutureOfAI #SecureAI #EmergingTechnology "
        "#ResearchInnovation"
    ),

    "Space Cybersecurity": (
        "#SpaceCybersecurity #SpaceSecurity "
        "#SatelliteSecurity #AerospaceCybersecurity "
        "#AIResearch #AgenticAI #AISecurity "
        "#ThreatIntelligence #SpaceTechnology "
        "#CyberDefense #SatelliteCommunications "
        "#CriticalInfrastructure #AIInnovation "
        "#PredictiveSecurity #FutureOfSpace"
    ),

    "OT and IoT Security": (
        "#OTSecurity #IoTSecurity #ICSecurity "
        "#IndustrialCybersecurity #AIThreatDetection "
        "#Cybersecurity #AISecurity #AgenticAI "
        "#CriticalInfrastructure #ThreatHunting "
        "#ZeroTrust #EdgeAI #AIResearch "
        "#PredictiveMaintenance #SecureAI"
    ),

    # 10. Practical AI Engineering and Experiments
    "AI Research Experiments": (
        "#AIResearch #AIExperiments #OpenSourceAI "
        "#MachineLearning #DeepLearning "
        "#AgenticAI #MultiAgentSystems #SwarmAI "
        "#Benchmarking #ModelEvaluation "
        "#ReproducibleResearch #AIEngineering "
        "#DataScience #AdvancedAI #Innovation"
    ),

    "Docker AI Security": (
        "#Docker #ContainerSecurity #AISecurity "
        "#AgenticAI #AIAgents #DevSecOps "
        "#CloudNativeSecurity #Cybersecurity "
        "#Sandboxing #RuntimeSecurity "
        "#ZeroTrust #AIResearch #SecureAI "
        "#Containerization #SecurityAutomation"
    ),

    "AI Cybersecurity Trust Engine": (
        "#AITrustEngine #AISecurity #Cybersecurity "
        "#AgenticAI #AISafety #AITrust "
        "#AIAlignment #AutonomousCyberDefense "
        "#MultiAgentSystems #PredictiveSecurity "
        "#ThreatIntelligence #AIResearch "
        "#ResponsibleAI #SecurityAutomation "
        "#TrustworthyAI"
    ),

    # 11. Default fallback
    "default": (
        "#AgenticAI #AISecurity #AIResearch "
        "#Cybersecurity #AIAgents #MultiAgentSystems "
        "#SwarmIntelligence #ASI #AGI "
        "#PredictiveIntelligence #AISafety "
        "#AITrust #ThreatIntelligence #DevSecOps "
        "#FutureOfAI"
    ),
}

# ── PDF Colors ────────────────────────────────────────────────────────────────
DARK_NAVY  = HexColor("#0A0E1A")
NAVY_PDF   = HexColor("#0D1528")
MID_BLUE   = HexColor("#1A2540")
CYAN_PDF   = HexColor("#00C8FF")
YELLOW_PDF = HexColor("#FFD700")
WHITE_PDF  = HexColor("#FFFFFF")
GRAY_PDF   = HexColor("#A0AABF")
LIGHT_GRAY = HexColor("#E8EDF5")

# ── Infographic Colors ────────────────────────────────────────────────────────
BG        = (8, 12, 28)
BG2       = (13, 17, 38)
BG3       = (18, 24, 52)
WHITE     = (255, 255, 255)
OFF_WHITE = (215, 225, 255)
GRAY      = (150, 160, 195)
DARK_GRAY = (38, 45, 78)

ACCENT_SETS = [
    {"P":(0,200,255),  "S":(0,255,180), "H":(255,220,0)},
    {"P":(180,80,255), "S":(255,50,150),"H":(255,220,0)},
    {"P":(50,220,255), "S":(0,180,255), "H":(255,150,50)},
    {"P":(50,255,150), "S":(0,220,120), "H":(255,220,0)},
    {"P":(255,130,50), "S":(220,80,0),  "H":(255,220,0)},
]

CELL_COLORS = [
    (0,200,255),(0,255,180),(255,220,0),
    (180,80,255),(255,150,50),(50,220,255),
    (50,255,150),(255,100,150),(100,200,100),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_hashtags(subtopic):
    for key in HASHTAG_SETS:
        if key.lower() in subtopic.lower():
            return HASHTAG_SETS[key]
    return HASHTAG_SETS["default"]

def get_daily_topic():
    day = datetime.now().timetuple().tm_yday
    return DAILY_TOPICS[day % len(DAILY_TOPICS)]

def get_seed(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)

def ft(text, n):
    text = str(text).strip()
    return text if len(text) <= n else text[:n-2]+".."

def text_in_box(draw, text, x, y, max_w, max_h, font, color,
                line_h=15, padding=3):
    text = str(text).strip()
    chars = max(1, (max_w-padding*2) // 7)
    lines = textwrap.fill(text, width=chars).split('\n')
    cy = y + padding
    for line in lines:
        if cy + line_h > y + max_h - padding:
            break
        draw.text((x+padding, cy), line, font=font, fill=color)
        cy += line_h

# ── Icons ─────────────────────────────────────────────────────────────────────

def draw_icon(draw, name, cx, cy, size, color):
    s = size
    x = cx - s//2
    y = cy - s//2
    if name == "shield":
        pts = [(cx,y),(x+s,y+s//3),(x+s,y+s*2//3),(cx,y+s),(x,y+s*2//3),(x,y+s//3)]
        draw.polygon(pts, outline=color, width=2)
    elif name == "brain":
        draw.ellipse([(x,y+s//4),(x+s,y+s*3//4)], outline=color, width=2)
        draw.line([(cx,y+s//4),(cx,y+s*3//4)], fill=color, width=1)
        draw.arc([(x+s//4,y),(x+s*3//4,y+s//2)], 180, 0, fill=color, width=2)
    elif name == "lock":
        draw.rectangle([(x+s//4,cy),(x+s*3//4,y+s)], outline=color, width=2)
        draw.arc([(x+s//4,y),(x+s*3//4,cy+s//6)], 180, 0, fill=color, width=2)
        draw.ellipse([(cx-3,cy+s//6-3),(cx+3,cy+s//6+3)], fill=color)
    elif name == "eye":
        draw.arc([(x,y+s//4),(x+s,y+s*3//4)], 0, 180, fill=color, width=2)
        draw.arc([(x,y+s//4),(x+s,y+s*3//4)], 180, 360, fill=color, width=2)
        draw.ellipse([(cx-s//6,cy-s//6),(cx+s//6,cy+s//6)], fill=color)
    elif name == "network":
        draw.ellipse([(cx-4,cy-4),(cx+4,cy+4)], fill=color)
        for ang in [0,72,144,216,288]:
            rad = math.radians(ang)
            ex = int(cx+s//2*math.cos(rad))
            ey = int(cy+s//2*math.sin(rad))
            draw.line([(cx,cy),(ex,ey)], fill=color, width=1)
            draw.ellipse([(ex-3,ey-3),(ex+3,ey+3)], fill=color)
    elif name == "warning":
        draw.polygon([(cx,y),(x+s,y+s),(x,y+s)], outline=color, width=2)
        draw.line([(cx,y+s//3),(cx,y+s*2//3)], fill=color, width=2)
        draw.ellipse([(cx-2,y+s*3//4-2),(cx+2,y+s*3//4+2)], fill=color)
    elif name == "gear":
        draw.ellipse([(cx-s//4,cy-s//4),(cx+s//4,cy+s//4)], outline=color, width=2)
        for ang in range(0,360,60):
            rad = math.radians(ang)
            x1 = int(cx+s//4*math.cos(rad)); y1 = int(cy+s//4*math.sin(rad))
            x2 = int(cx+s//2*math.cos(rad)); y2 = int(cy+s//2*math.sin(rad))
            draw.line([(x1,y1),(x2,y2)], fill=color, width=3)
    elif name == "check":
        draw.ellipse([(x,y),(x+s,y+s)], outline=color, width=2)
        draw.line([(x+s//4,cy),(x+s*2//5,y+s*2//3),(x+s*3//4,y+s//3)],
                  fill=color, width=2)
    elif name == "search":
        draw.ellipse([(x,y),(x+s*2//3,y+s*2//3)], outline=color, width=2)
        draw.line([(x+s*2//3-3,y+s*2//3-3),(x+s,y+s)], fill=color, width=3)
    elif name == "monitor":
        draw.rectangle([(x,y),(x+s,y+s*3//4)], outline=color, width=2)
        draw.line([(cx,y+s*3//4),(cx,y+s)], fill=color, width=2)
        draw.line([(x+s//4,y+s),(x+s*3//4,y+s)], fill=color, width=2)
    elif name == "robot":
        draw.rectangle([(x+s//4,y),(x+s*3//4,y+s//3)], outline=color, width=2)
        draw.rectangle([(x+s//6,y+s//3),(x+s*5//6,y+s*5//6)],
                       outline=color, width=2)
        draw.ellipse([(cx-s//4-3,y+s//6-3),(cx-s//4+3,y+s//6+3)], fill=color)
        draw.ellipse([(cx+s//4-3,y+s//6-3),(cx+s//4+3,y+s//6+3)], fill=color)
    elif name == "database":
        draw.ellipse([(x,y),(x+s,y+s//4)], outline=color, width=2)
        draw.line([(x,y+s//8),(x,y+s*3//4)], fill=color, width=2)
        draw.line([(x+s,y+s//8),(x+s,y+s*3//4)], fill=color, width=2)
        draw.arc([(x,y+s//2),(x+s,y+s)], 0, 180, fill=color, width=2)
        draw.arc([(x,y+s//4),(x+s,y+s*5//8)], 0, 180, fill=color, width=2)

# ── AI: LinkedIn Post ─────────────────────────────────────────────────────────

def ai_generate_post(subtopic):
    hashtags = get_hashtags(subtopic)
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content":
                "You are Aurobinda Ojha, Independent Researcher on Cybersecurity "
                "and Agentic AI. Write deep technical LinkedIn posts. "
                "NEVER write any about me, reach out, or contact section. "
                "NEVER use ##, **, __, or any markdown. Plain text + emojis only."},
            {"role": "user", "content":
                f"Write a detailed LinkedIn post about: {subtopic}\n\n"
                f"STRUCTURE:\n"
                f"1. Hook: emoji + powerful title\n"
                f"2. 2-3 context lines\n"
                f"3. Problem list (5-6 emoji bullets)\n"
                f"4. Powerful insight\n"
                f"5. Solution list (5 bullets)\n"
                f"6. ASCII architecture with | arrows\n"
                f"7. Four technical sections with emoji headers\n"
                f"8. Goals (5-6 checkmarks)\n"
                f"9. Preferred Stack\n"
                f"10. Future vision\n\n"
                f"STRICT RULES:\n"
                f"- NO about me, NO contact info\n"
                f"- NO markdown at all\n"
                f"- Plain text + emojis only\n"
                f"- 400-500 words\n\n"
                f"After the post content add EXACTLY this hashtag line:\n"
                f"{hashtags}"}
        ],
        max_tokens=1500,
    )
    content = response.choices[0].message.content.strip()
    for ch in ["##","**","__","# ","* "]:
        content = content.replace(ch, "")
    skip_kw = ["reach out","contact me","about me","i am aurobinda",
                "aurobindaojha@","gmail.com","collaborat","freelance"]
    lines = [l for l in content.split('\n')
             if not any(k in l.lower() for k in skip_kw)]
    content = '\n'.join(lines).strip()
    if hashtags.split()[0] not in content:
        content = content + "\n\n" + hashtags
    return content

def ai_generate_pdf_post(subtopic, book_title):
    """Shorter post specifically for the PDF document post"""
    hashtags = get_hashtags(subtopic)
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content":
                "You are Aurobinda Ojha, Independent Researcher on Cybersecurity "
                "and Agentic AI. Write short engaging LinkedIn posts. "
                "NEVER use ##, **, __, or markdown. Plain text + emojis only."},
            {"role": "user", "content":
                f"Write a SHORT LinkedIn post (150-200 words) to share a PDF guide about: {subtopic}\n\n"
                f"Book title: {book_title}\n\n"
                f"STRUCTURE:\n"
                f"1. Hook line with emoji\n"
                f"2. 2-3 lines why this PDF matters\n"
                f"3. 4-5 bullet points of what's inside\n"
                f"4. Call to action to read/save\n\n"
                f"End with:\n{hashtags}\n\n"
                f"NO markdown. Plain text + emojis only."}
        ],
        max_tokens=500,
    )
    content = response.choices[0].message.content.strip()
    for ch in ["##","**","__","# ","* "]:
        content = content.replace(ch, "")
    if hashtags.split()[0] not in content:
        content = content + "\n\n" + hashtags
    return content

# ── AI: Infographic Data ──────────────────────────────────────────────────────

def ai_generate_infographic_data(subtopic):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Create infographic data for: {subtopic}\n\n"
                f"Reply JSON only:\n"
                f"{{\n"
                f"  \"main_title\": \"TOPIC COMPLETE DEEP DIVE (caps max 5 words)\",\n"
                f"  \"tagline\": \"tagline max 8 words\",\n"
                f"  \"top_badges\": [\n"
                f"    {{\"icon\":\"shield\",\"label\":\"max 2 words\"}},\n"
                f"    {{\"icon\":\"eye\",\"label\":\"max 2 words\"}},\n"
                f"    {{\"icon\":\"monitor\",\"label\":\"max 2 words\"}},\n"
                f"    {{\"icon\":\"warning\",\"label\":\"max 2 words\"}}\n"
                f"  ],\n"
                f"  \"sections\": [\n"
                f"    {{\n"
                f"      \"number\": 1,\n"
                f"      \"title\": \"Section Title max 4 words\",\n"
                f"      \"icon\": \"one of: shield,brain,lock,eye,network,warning,gear,check,search,monitor,robot,database\",\n"
                f"      \"bullets\": [\"max 4 words\",\"max 4 words\",\"max 4 words\",\"max 4 words\"]\n"
                f"    }}\n"
                f"  ],\n"
                f"  \"bottom_quote\": \"Powerful closing quote max 10 words\"\n"
                f"}}\n\n"
                f"Exactly 9 sections. Each has exactly 4 short bullets.\n"
                f"Make everything specific to {subtopic}."}
        ],
        max_tokens=1500,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json","").replace("```","").strip()
    return json.loads(raw)

# ── AI: Book Content for PDF ──────────────────────────────────────────────────

def ai_generate_book_content(subtopic):
    print(f"Generating book content for: {subtopic}")
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content":
                "You are Aurobinda Ojha, Independent Researcher on Cybersecurity "
                "and Agentic AI. Create structured technical book content."},
            {"role": "user", "content":
                f"Create detailed book content about: {subtopic}\n\n"
                f"Reply JSON only:\n"
                f"{{\n"
                f"  \"title\": \"TOPIC COMPLETE DEEP DIVE (caps max 5 words)\",\n"
                f"  \"subtitle\": \"subtitle max 8 words\",\n"
                f"  \"tagline\": \"tagline max 10 words\",\n"
                f"  \"about\": \"2 sentences about this topic and why it matters\",\n"
                f"  \"who_can\": [\"audience1\",\"audience2\",\"audience3\",\"audience4\",\"audience5\"],\n"
                f"  \"why_us\": [\"benefit1 max 8 words\",\"benefit2\",\"benefit3\",\"benefit4\",\"benefit5\"],\n"
                f"  \"chapters\": [\n"
                f"    {{\n"
                f"      \"number\": 1,\n"
                f"      \"title\": \"Chapter Title max 5 words\",\n"
                f"      \"sections\": [\n"
                f"        {{\n"
                f"          \"heading\": \"Section heading max 5 words\",\n"
                f"          \"bullets\": [\"point max 8 words\",\"point\",\"point\",\"point\"]\n"
                f"        }}\n"
                f"      ]\n"
                f"    }}\n"
                f"  ],\n"
                f"  \"key_concepts\": [\n"
                f"    {{\"term\": \"Term\", \"definition\": \"Definition max 15 words\"}}\n"
                f"  ],\n"
                f"  \"tools\": [\"tool1\",\"tool2\",\"tool3\",\"tool4\",\"tool5\",\"tool6\",\"tool7\",\"tool8\"],\n"
                f"  \"conclusion\": \"Powerful closing statement 2-3 sentences\"\n"
                f"}}\n\n"
                f"chapters: exactly 6. Each has 3-4 sections, each section 4 bullets.\n"
                f"key_concepts: exactly 6.\n"
                f"Make everything specific to {subtopic}."}
        ],
        max_tokens=3000,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json","").replace("```","").strip()
    return json.loads(raw)

# ── Fonts ─────────────────────────────────────────────────────────────────────

def load_fonts():
    try:
        B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return {
            "h1":   ImageFont.truetype(B, 52),
            "h2":   ImageFont.truetype(B, 36),
            "h3":   ImageFont.truetype(B, 24),
            "h4":   ImageFont.truetype(B, 18),
            "h5":   ImageFont.truetype(B, 14),
            "body": ImageFont.truetype(R, 14),
            "sm":   ImageFont.truetype(R, 12),
            "xs":   ImageFont.truetype(R, 11),
        }
    except:
        d = ImageFont.load_default()
        return {k: d for k in ["h1","h2","h3","h4","h5","body","sm","xs"]}

# ── Draw Helpers ──────────────────────────────────────────────────────────────

def rbox(draw, x0, y0, x1, y1, fill=None, outline=None, r=6, w=1):
    try:
        draw.rounded_rectangle([(x0,y0),(x1,y1)],
                                radius=r, fill=fill,
                                outline=outline, width=w)
    except:
        draw.rectangle([(x0,y0),(x1,y1)],
                       fill=fill, outline=outline, width=w)

def cx_text(draw, text, cx, y, font, color):
    bbox = draw.textbbox((0,0), text, font=font)
    w = bbox[2]-bbox[0]
    draw.text((cx-w//2, y), text, font=font, fill=color)

# ── Profile Image (Pillow) ────────────────────────────────────────────────────

def load_profile_image(size=110):
    try:
        resp = requests.get(PROFILE_IMAGE_URL, timeout=15)
        resp.raise_for_status()
        profile = Image.open(io.BytesIO(resp.content)).convert("RGB")
        profile = profile.resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        md = ImageDraw.Draw(mask)
        md.ellipse([(0,0),(size,size)], fill=255)
        result = Image.new("RGBA", (size, size), (0,0,0,0))
        result.paste(profile, (0,0))
        result.putalpha(mask)
        print("Profile image loaded!")
        return result
    except Exception as e:
        print(f"Profile image failed: {e}")
        return None

# ── Profile Image (ReportLab) ─────────────────────────────────────────────────

def get_profile_image_rl(size_mm=32):
    try:
        resp = requests.get(PROFILE_IMAGE_URL, timeout=15)
        resp.raise_for_status()
        img = PILImage.open(io.BytesIO(resp.content)).convert("RGB")
        size_px = 200
        img = img.resize((size_px, size_px), PILImage.LANCZOS)
        mask = PILImage.new("L", (size_px, size_px), 0)
        md = ImageDraw.Draw(mask)
        md.ellipse([(0,0),(size_px,size_px)], fill=255)
        result = PILImage.new("RGBA", (size_px, size_px), (13,21,40,255))
        result.paste(img, (0,0))
        result.putalpha(mask)
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        buf.seek(0)
        sz = size_mm * mm
        return RLImage(buf, width=sz, height=sz)
    except Exception as e:
        print(f"Profile RL image failed: {e}")
        return None

# ── PDF Builder ───────────────────────────────────────────────────────────────

def build_pdf(subtopic, book_data, output_path):
    print(f"Building PDF: {output_path}")
    W, H = A4
    profile_rl = get_profile_image_rl(size_mm=32)

    def page_bg(canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.setFillColor(DARK_NAVY)
        canvas_obj.rect(0, 0, W, H, fill=1, stroke=0)
        canvas_obj.setStrokeColor(HexColor("#0F1825"))
        canvas_obj.setLineWidth(0.3)
        for x in range(0, int(W), 20):
            canvas_obj.line(x, 0, x, H)
        for y in range(0, int(H), 20):
            canvas_obj.line(0, y, W, y)
        canvas_obj.setFillColor(CYAN_PDF)
        canvas_obj.rect(0, H-8, W, 8, fill=1, stroke=0)
        canvas_obj.setFillColor(NAVY_PDF)
        canvas_obj.rect(0, H-35, W, 27, fill=1, stroke=0)
        canvas_obj.setFillColor(CYAN_PDF)
        canvas_obj.setFont("Helvetica-Bold", 9)
        canvas_obj.drawString(15, H-26, book_data.get("title","")[:50])
        canvas_obj.setFillColor(GRAY_PDF)
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawRightString(W-15, H-26, "aurobindaojha.com")
        canvas_obj.setFillColor(NAVY_PDF)
        canvas_obj.rect(0, 0, W, 22, fill=1, stroke=0)
        canvas_obj.setFillColor(CYAN_PDF)
        canvas_obj.rect(0, 22, W, 2, fill=1, stroke=0)
        canvas_obj.setFillColor(GRAY_PDF)
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.drawString(15, 8,
            "Aurobinda Ojha | Independent Researcher | Cybersecurity & Agentic AI")
        canvas_obj.setFillColor(CYAN_PDF)
        canvas_obj.drawRightString(W-15, 8, f"Page {doc.page}")
        canvas_obj.restoreState()

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=40*mm, bottomMargin=28*mm,
        title=book_data.get("title",""),
        author="Aurobinda Ojha",
    )
    story = []

    # Cover
    story.append(Spacer(1, 20*mm))
    if profile_rl:
        t = Table([[profile_rl]], colWidths=[W-30*mm])
        t.setStyle(TableStyle([
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("BACKGROUND",(0,0),(-1,-1),DARK_NAVY),
        ]))
        story.append(t)
        story.append(Spacer(1, 5*mm))
    story.append(Paragraph("AUROBINDA OJHA",
        ParagraphStyle("ca", fontSize=13, textColor=CYAN_PDF,
                       alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=2)))
    story.append(Paragraph(
        "Independent Researcher | Cybersecurity &amp; Agentic AI",
        ParagraphStyle("cr", fontSize=9, textColor=GRAY_PDF,
                       alignment=TA_CENTER, fontName="Helvetica", spaceAfter=8)))
    story.append(HRFlowable(width="60%", thickness=1, color=CYAN_PDF, spaceAfter=8))
    title = book_data.get("title","AI SECURITY DEEP DIVE")
    words = title.split()
    mid   = max(1, len(words)//2)
    story.append(Paragraph(" ".join(words[:mid]),
        ParagraphStyle("ct1", fontSize=36, textColor=WHITE_PDF,
                       alignment=TA_CENTER, fontName="Helvetica-Bold",
                       spaceAfter=0, leading=40)))
    story.append(Paragraph(" ".join(words[mid:]),
        ParagraphStyle("ct2", fontSize=36, textColor=CYAN_PDF,
                       alignment=TA_CENTER, fontName="Helvetica-Bold",
                       spaceAfter=6, leading=40)))
    story.append(Paragraph(book_data.get("subtitle",""),
        ParagraphStyle("cs", fontSize=13, textColor=YELLOW_PDF,
                       alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=4)))
    story.append(Paragraph(book_data.get("tagline","").upper(),
        ParagraphStyle("ct", fontSize=9, textColor=GRAY_PDF,
                       alignment=TA_CENTER, fontName="Helvetica", spaceAfter=10)))
    story.append(HRFlowable(width="80%", thickness=1, color=MID_BLUE, spaceAfter=6))
    story.append(Paragraph(datetime.now().strftime("%B %Y"),
        ParagraphStyle("cd", fontSize=9, textColor=GRAY_PDF,
                       alignment=TA_CENTER, fontName="Helvetica")))
    story.append(PageBreak())

    # About
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("ABOUT",
        ParagraphStyle("ah", fontSize=32, textColor=WHITE_PDF,
                       fontName="Helvetica-Bold", spaceAfter=3)))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_BLUE, spaceAfter=6))
    story.append(Paragraph(book_data.get("about",""),
        ParagraphStyle("ab", fontSize=11, textColor=LIGHT_GRAY,
                       fontName="Helvetica", leading=16,
                       alignment=TA_JUSTIFY, spaceAfter=8)))
    who_items = "".join(f"&bull; {w}<br/>" for w in book_data.get("who_can",[]))
    why_items = "".join(f"&bull; {w}<br/>" for w in book_data.get("why_us",[]))
    PW = A4[0] - 30*mm
    who_col = [
        Paragraph("WHO CAN?", ParagraphStyle("wh", fontSize=13,
            textColor=CYAN_PDF, fontName="Helvetica-Bold", spaceAfter=4)),
        Paragraph(who_items, ParagraphStyle("wb", fontSize=9,
            textColor=WHITE_PDF, fontName="Helvetica", leading=14)),
    ]
    why_col = [
        Paragraph("WHY US?", ParagraphStyle("ywh", fontSize=13,
            textColor=YELLOW_PDF, fontName="Helvetica-Bold", spaceAfter=4)),
        Paragraph(why_items, ParagraphStyle("ywb", fontSize=9,
            textColor=WHITE_PDF, fontName="Helvetica", leading=14)),
    ]
    t2 = Table([[who_col, why_col]], colWidths=[PW*0.48, PW*0.52])
    t2.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("BACKGROUND",(0,0),(0,0),NAVY_PDF),
        ("BACKGROUND",(1,0),(1,0),NAVY_PDF),
        ("BOX",(0,0),(0,0),1,CYAN_PDF),
        ("BOX",(1,0),(1,0),1,YELLOW_PDF),
        ("LEFTPADDING",(0,0),(-1,-1),8),
        ("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
    ]))
    story.append(t2)
    story.append(PageBreak())

    # Chapters
    for chapter in book_data.get("chapters",[]):
        story.append(Spacer(1, 8*mm))
        story.append(Paragraph(
            f"{chapter.get('number',1)}. {chapter.get('title','')}",
            ParagraphStyle("ch", fontSize=20, textColor=CYAN_PDF,
                           fontName="Helvetica-Bold", spaceAfter=4, leading=24)))
        story.append(HRFlowable(width="100%", thickness=1,
                                 color=MID_BLUE, spaceAfter=6))
        for sec in chapter.get("sections",[]):
            story.append(Paragraph(sec.get("heading",""),
                ParagraphStyle("sh", fontSize=12, textColor=YELLOW_PDF,
                               fontName="Helvetica-Bold",
                               spaceAfter=3, spaceBefore=6)))
            for bullet in sec.get("bullets",[]):
                story.append(Paragraph(f"&bull;  {bullet}",
                    ParagraphStyle("sb", fontSize=10, textColor=WHITE_PDF,
                                   fontName="Helvetica", leading=14,
                                   leftIndent=10, spaceAfter=2)))
            story.append(Spacer(1, 3*mm))
        story.append(PageBreak())

    # Key Concepts
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("KEY CONCEPTS",
        ParagraphStyle("kh", fontSize=24, textColor=WHITE_PDF,
                       fontName="Helvetica-Bold", spaceAfter=4)))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_PDF, spaceAfter=8))
    PW2 = A4[0] - 30*mm
    for concept in book_data.get("key_concepts",[]):
        row = Table([[
            Paragraph(concept.get("term",""),
                ParagraphStyle("kt", fontSize=11, textColor=CYAN_PDF,
                               fontName="Helvetica-Bold")),
            Paragraph(concept.get("definition",""),
                ParagraphStyle("kd", fontSize=10, textColor=WHITE_PDF,
                               fontName="Helvetica", leading=14))
        ]], colWidths=[PW2*0.28, PW2*0.72])
        row.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),NAVY_PDF),
            ("BOX",(0,0),(-1,-1),1,MID_BLUE),
            ("LINEAFTER",(0,0),(0,0),1,CYAN_PDF),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),8),
            ("RIGHTPADDING",(0,0),(-1,-1),8),
            ("TOPPADDING",(0,0),(-1,-1),6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ]))
        story.append(row)
        story.append(Spacer(1, 2*mm))
    story.append(PageBreak())

    # Tools
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("TOOLS &amp; STACK",
        ParagraphStyle("th", fontSize=24, textColor=WHITE_PDF,
                       fontName="Helvetica-Bold", spaceAfter=4)))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_PDF, spaceAfter=8))
    tools = book_data.get("tools",[])
    cols  = 4
    PW3   = A4[0] - 30*mm
    rows_t = [tools[i:i+cols] for i in range(0, len(tools), cols)]
    td    = []
    for row in rows_t:
        while len(row) < cols:
            row.append("")
        td.append([Paragraph(t3, ParagraphStyle("tc", fontSize=10,
            textColor=CYAN_PDF if t3 else WHITE_PDF,
            fontName="Helvetica-Bold", alignment=TA_CENTER))
            for t3 in row])
    if td:
        tt = Table(td, colWidths=[PW3/cols]*cols)
        tt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),NAVY_PDF),
            ("BOX",(0,0),(-1,-1),1,MID_BLUE),
            ("INNERGRID",(0,0),(-1,-1),0.5,MID_BLUE),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),10),
            ("BOTTOMPADDING",(0,0),(-1,-1),10),
        ]))
        story.append(tt)
    story.append(PageBreak())

    # Conclusion
    story.append(Spacer(1, 15*mm))
    story.append(Paragraph("CONCLUSION",
        ParagraphStyle("cnh", fontSize=28, textColor=WHITE_PDF,
                       fontName="Helvetica-Bold", spaceAfter=4,
                       alignment=TA_CENTER)))
    story.append(HRFlowable(width="60%", thickness=1, color=CYAN_PDF, spaceAfter=10))
    story.append(Paragraph(book_data.get("conclusion",""),
        ParagraphStyle("cnb", fontSize=12, textColor=LIGHT_GRAY,
                       fontName="Helvetica", leading=18,
                       alignment=TA_JUSTIFY, spaceAfter=15)))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_BLUE, spaceAfter=10))
    if profile_rl:
        ar = Table([[
            profile_rl,
            [
                Paragraph("AUROBINDA OJHA",
                    ParagraphStyle("an", fontSize=14, textColor=CYAN_PDF,
                                   fontName="Helvetica-Bold", spaceAfter=3)),
                Paragraph("Independent Researcher",
                    ParagraphStyle("ar1", fontSize=10, textColor=WHITE_PDF,
                                   fontName="Helvetica", spaceAfter=2)),
                Paragraph("Cybersecurity &amp; Agentic AI",
                    ParagraphStyle("ar2", fontSize=10, textColor=YELLOW_PDF,
                                   fontName="Helvetica", spaceAfter=4)),
                Paragraph("aurobindaojha@gmail.com",
                    ParagraphStyle("ae", fontSize=9, textColor=GRAY_PDF,
                                   fontName="Helvetica")),
            ]
        ]], colWidths=[35*mm, A4[0]-65*mm])
        ar.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("BACKGROUND",(0,0),(-1,-1),NAVY_PDF),
            ("BOX",(0,0),(-1,-1),1,CYAN_PDF),
            ("LEFTPADDING",(0,0),(-1,-1),8),
            ("RIGHTPADDING",(0,0),(-1,-1),8),
            ("TOPPADDING",(0,0),(-1,-1),8),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ]))
        story.append(ar)
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(
        "#AgenticAI  #Cybersecurity  #ZeroTrust  "
        "#AISecurity  #LLMOps  #AIOps  #MLOps  #AIAgents",
        ParagraphStyle("ht", fontSize=8, textColor=MID_BLUE,
                       fontName="Helvetica", alignment=TA_CENTER)))

    doc.build(story, onFirstPage=page_bg, onLaterPages=page_bg)
    print(f"PDF saved: {output_path}")

# ── LinkedIn: Upload PDF Document ─────────────────────────────────────────────

def upload_pdf_to_linkedin(pdf_path, title, description):
    """Upload PDF as a LinkedIn document post"""
    print(f"[{datetime.now()}] Uploading PDF to LinkedIn...")

    # Step 1 — Register upload
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-document"],
            "owner": f"urn:li:person:{LINKEDIN_PERSON_ID}",
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }
    r = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=LINKEDIN_HEADERS,
        json=register_payload
    )
    r.raise_for_status()
    rj = r.json()
    upload_url = rj["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset = rj["value"]["asset"]
    print(f"PDF asset registered: {asset}")

    # Step 2 — Upload PDF bytes
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    upload_r = requests.put(
        upload_url,
        headers={
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/octet-stream",
        },
        data=pdf_bytes
    )
    upload_r.raise_for_status()
    print(f"PDF uploaded! Asset: {asset}")
    return asset

def publish_pdf_post(pdf_asset, post_text, title):
    """Publish LinkedIn post with PDF document"""
    print(f"[{datetime.now()}] Publishing PDF post...")
    payload = {
        "author": f"urn:li:person:{LINKEDIN_PERSON_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text[:3000]},
                "shareMediaCategory": "DOCUMENT",
                "media": [{
                    "status": "READY",
                    "media": pdf_asset,
                    "title": {"text": title[:100]},
                    "description": {"text": "Complete Deep Dive Guide"}
                }]
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    r = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=LINKEDIN_HEADERS,
        json=payload
    )
    r.raise_for_status()
    post_id = r.json().get("id")
    print(f"PDF post published! ID: {post_id}")
    return post_id

# ── LinkedIn: Upload Image ────────────────────────────────────────────────────

def upload_image_to_linkedin(image_data):
    print(f"[{datetime.now()}] Uploading image to LinkedIn...")
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": f"urn:li:person:{LINKEDIN_PERSON_ID}",
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }
    r = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=LINKEDIN_HEADERS, json=register_payload
    )
    r.raise_for_status()
    rj = r.json()
    upload_url = rj["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset = rj["value"]["asset"]
    requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
                 "Content-Type": "application/octet-stream"},
        data=image_data
    ).raise_for_status()
    print(f"Image uploaded! Asset: {asset}")
    return asset

# ── Infographic Creator ───────────────────────────────────────────────────────

def create_infographic(subtopic, data):
    print(f"[{datetime.now()}] Creating infographic...")

    W       = 1080
    seed    = get_seed(subtopic)
    C       = ACCENT_SETS[seed % len(ACCENT_SETS)]
    P, S, H = C["P"], C["S"], C["H"]
    fonts   = load_fonts()
    profile_img = load_profile_image(size=120)

    COLS   = 3
    ROWS   = 3
    PAD    = 8
    CELL_W = (W-(COLS+1)*PAD)//COLS
    CELL_H = 290
    GRID_H = ROWS*CELL_H+(ROWS+1)*PAD
    H_HDR  = 190
    H_BADGE= 55
    H_TAG  = 38
    H_FOOT = 85
    TOTAL_H= H_HDR+H_BADGE+H_TAG+GRID_H+H_FOOT

    img  = Image.new("RGB", (W, TOTAL_H), BG)
    draw = ImageDraw.Draw(img)

    for y in range(TOTAL_H):
        t = y/TOTAL_H
        draw.line([(0,y),(W,y)], fill=(
            int(BG[0]+t*5), int(BG[1]+t*5), int(BG[2]+t*8)))
    for x in range(0, W, 45):
        draw.line([(x,0),(x,TOTAL_H)], fill=(13,17,38), width=1)
    for y in range(0, TOTAL_H, 45):
        draw.line([(0,y),(W,y)], fill=(13,17,38), width=1)

    Y = 0

    # Header gradient
    for y in range(H_HDR):
        t = y/H_HDR
        r = int(P[0]*0.5*(1-t)+BG[0]*t)
        g = int(P[1]*0.5*(1-t)+BG[1]*t)
        b = int(P[2]*0.5*(1-t)+BG[2]*t)
        draw.line([(0,Y+y),(W,Y+y)], fill=(
            max(0,min(255,r)),max(0,min(255,g)),max(0,min(255,b))))

    PROF_SIZE = 120
    PROF_X    = W - PROF_SIZE - 20
    PROF_Y    = Y + 20
    if profile_img is not None:
        img_rgba = img.convert("RGBA")
        img_rgba.paste(profile_img, (PROF_X, PROF_Y), profile_img)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)
        draw.ellipse([(PROF_X-4,PROF_Y-4),
                      (PROF_X+PROF_SIZE+4,PROF_Y+PROF_SIZE+4)],
                     outline=P, width=3)

    draw.text((PROF_X-10, PROF_Y+PROF_SIZE+8), "AUROBINDA OJHA",
              font=fonts["h5"], fill=WHITE)
    draw.text((PROF_X-10, PROF_Y+PROF_SIZE+26), "Cybersecurity Expert",
              font=fonts["xs"], fill=P)

    title_max_w = PROF_X - 30
    title = data.get("main_title","AI SECURITY DEEP DIVE")
    words = title.split()
    mid   = max(1, len(words)//2)
    l1    = " ".join(words[:mid])
    l2    = " ".join(words[mid:])
    while draw.textbbox((0,0),l1,font=fonts["h1"])[2] > title_max_w:
        l1 = l1[:max(5,len(l1)-3)]+".."; break
    while draw.textbbox((0,0),l2,font=fonts["h1"])[2] > title_max_w:
        l2 = l2[:max(5,len(l2)-3)]+".."; break

    draw.text((18, Y+18), l1, font=fonts["h1"], fill=WHITE)
    draw.text((18, Y+75), l2, font=fonts["h1"], fill=P)
    bb = draw.textbbox((0,0), l2, font=fonts["h1"])
    draw.rectangle([(18,Y+130),(18+min(bb[2]-bb[0]+30,title_max_w),Y+134)], fill=H)
    draw.text((20, Y+142), "CYBERSECURITY RESEARCHER & AGENTIC AI EXPERT",
              font=fonts["xs"], fill=GRAY)
    Y += H_HDR

    # Badges
    rbox(draw, 0, Y, W, Y+H_BADGE, fill=(13,17,40))
    badges = data.get("top_badges",[])[:4]
    bw = W // max(len(badges),1)
    for i, badge in enumerate(badges):
        bcx = i*bw + bw//2
        draw_icon(draw, badge.get("icon","shield"), bcx-40, Y+H_BADGE//2, 18, P)
        draw.text((bcx-20, Y+H_BADGE//2-7), ft(badge.get("label",""),14),
                  font=fonts["sm"], fill=WHITE)
        if i < len(badges)-1:
            draw.line([((i+1)*bw,Y+10),((i+1)*bw,Y+H_BADGE-10)],
                      fill=DARK_GRAY, width=1)
    Y += H_BADGE

    # Tagline
    rbox(draw, 0, Y, W, Y+H_TAG, fill=(10,13,32))
    cx_text(draw, data.get("tagline","").upper(), W//2, Y+11, fonts["xs"], GRAY)
    Y += H_TAG

    # Grid
    sections = data.get("sections",[])[:9]
    for idx, section in enumerate(sections):
        col   = idx % COLS
        row   = idx // COLS
        cx    = PAD + col*(CELL_W+PAD)
        cy    = Y + PAD + row*(CELL_H+PAD)
        color = CELL_COLORS[idx % len(CELL_COLORS)]

        rbox(draw, cx, cy, cx+CELL_W, cy+CELL_H, fill=BG2, outline=color, r=8, w=2)
        rbox(draw, cx, cy, cx+CELL_W, cy+48, fill=BG3, r=8, w=0)
        draw.rectangle([(cx,cy+38),(cx+CELL_W,cy+48)], fill=BG2)

        draw.ellipse([(cx+8,cy+8),(cx+30,cy+30)], fill=color)
        num  = str(section.get("number",idx+1))
        bbox = draw.textbbox((0,0), num, font=fonts["h5"])
        nw   = bbox[2]-bbox[0]
        draw.text((cx+19-nw//2, cy+12), num, font=fonts["h5"], fill=(0,0,0))
        draw.text((cx+38, cy+12), ft(section.get("title",""),24),
                  font=fonts["h5"], fill=color)

        ICON_Y = cy+50
        draw_icon(draw, section.get("icon","shield"),
                  cx+CELL_W//2, ICON_Y+16, 24, color)
        draw.line([(cx+8,ICON_Y+36),(cx+CELL_W-8,ICON_Y+36)],
                  fill=DARK_GRAY, width=1)

        by = ICON_Y + 44
        for bullet in section.get("bullets",[])[:4]:
            if by+16 > cy+CELL_H-8:
                break
            draw.ellipse([(cx+10,by+4),(cx+16,by+10)], fill=color)
            text_in_box(draw, ft(bullet,30), cx+20, by, CELL_W-28, 18,
                        fonts["sm"], OFF_WHITE, line_h=14, padding=2)
            by += 20

    Y += GRID_H

    # Footer
    draw.rectangle([(0,Y),(W,Y+H_FOOT)], fill=(7,9,22))
    draw.rectangle([(0,Y),(W,Y+3)], fill=P)
    if profile_img is not None:
        small = profile_img.resize((48,48), Image.LANCZOS)
        img_rgba = img.convert("RGBA")
        img_rgba.paste(small, (15, Y+18), small)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)
        draw.ellipse([(13,Y+16),(65,Y+68)], outline=P, width=2)
        draw.text((72, Y+22), "AUROBINDA OJHA", font=fonts["h5"], fill=WHITE)
        draw.text((72, Y+40),
                  "Independent Researcher | Cybersecurity & Agentic AI",
                  font=fonts["xs"], fill=GRAY)
    quote = data.get("bottom_quote","Secure AI. Protect the Future.")
    cx_text(draw, f'"{ft(quote,55)}"', W//2, Y+30, fonts["sm"], P)
    rbox(draw, W-100, Y+22, W-58, Y+56, fill=(0,119,181), r=6, w=0)
    cx_text(draw, "in", W-79, Y+30, fonts["h5"], WHITE)
    rbox(draw, W-52, Y+22, W-10, Y+56, fill=(200,0,0), r=6, w=0)
    cx_text(draw, "▶", W-31, Y+30, fonts["h5"], WHITE)
    draw.rectangle([(0,Y+H_FOOT-3),(W,Y+H_FOOT)], fill=P)

    img = img.crop((0, 0, W, TOTAL_H))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=96)
    buf.seek(0)
    print("Infographic created!")
    return buf.read()

# ── Main ──────────────────────────────────────────────────────────────────────

def job_post():
    subtopic = get_daily_topic()
    print(f"[{datetime.now()}] Today: {subtopic}")

    # ── POST 1: Image post ────────────────────────────────────────────────
    print(f"[{datetime.now()}] === POST 1: Infographic Image ===")
    content = ai_generate_post(subtopic)
    print(f"Post: {content[:100]}...")

    data = ai_generate_infographic_data(subtopic)
    print(f"Infographic title: {data.get('main_title')}")

    image_data = create_infographic(subtopic, data)
    asset = upload_image_to_linkedin(image_data)

    payload = {
        "author": f"urn:li:person:{LINKEDIN_PERSON_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content[:3000]},
                "shareMediaCategory": "IMAGE",
                "media": [{
                    "status": "READY",
                    "description": {"text": data.get("main_title", subtopic)},
                    "media": asset,
                    "title": {"text": data.get("main_title", subtopic)[:100]}
                }]
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    r = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=LINKEDIN_HEADERS, json=payload
    )
    r.raise_for_status()
    print(f"[{datetime.now()}] Image post published! ID: {r.json().get('id')}")

    # ── POST 2: PDF Document post ─────────────────────────────────────────
    print(f"[{datetime.now()}] === POST 2: PDF Document ===")
    try:
        book_data = ai_generate_book_content(subtopic)
        book_title = book_data.get("title", subtopic)
        print(f"Book title: {book_title}")

        safe = subtopic.lower().replace(" ","_").replace("/","_")[:35]
        pdf_path = f"/tmp/{safe}.pdf"
        build_pdf(subtopic, book_data, pdf_path)

        pdf_asset = upload_pdf_to_linkedin(pdf_path, book_title,
                                           book_data.get("subtitle",""))

        pdf_post_text = ai_generate_pdf_post(subtopic, book_title)
        publish_pdf_post(pdf_asset, pdf_post_text, book_title)

        print(f"[{datetime.now()}] PDF post published!")

    except Exception as e:
        print(f"[{datetime.now()}] PDF post failed: {e}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
