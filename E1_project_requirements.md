# DSAA 4040 Course Project Requirements

Course: Cloud Computing & Big Data Systems  
Instructor: Guoming Tang  
Term: Spring 2026, HKUST(GZ)  
Selected Topic: E1. Design and Deploy a Cloud-Native Online Bookstore on Kubernetes  
Handout updated: May 6, 2026

## 1. Project Track

This project follows the engineering-oriented track.

Engineering-oriented projects focus on:

- designing a working system
- implementing the core application
- containerizing and deploying it
- demonstrating the deployed system
- testing or evaluating the system behavior

## 2. Team Requirement

Recommended team size:

- 1-2 students per group
- 3 students are allowed with justification

## 3. Recommended Environment

For Kubernetes-based projects, lightweight local environments are acceptable:

- Minikube
- Docker Desktop Kubernetes
- K3s

Using a more complicated environment does not provide extra credit by itself.

## 4. Required Deliverables

The final submission should include:

- source code and configuration files
- project report in PDF format
- proposal, presentation slides, and demo video
- README with setup and reproduction instructions

## 5. Engineering Report Format

The report should be written as a technical report and include:

- Problem Statement
- System Design
- Implementation
- Deployment / Demo
- Evaluation or Testing
- Limitations and Future Work
- References

## 6. E1 Project: Cloud-Native Online Bookstore

### Goal

Design and implement a small cloud-native online bookstore and deploy it on Kubernetes.

### Suggested Technology Stack

- Kubernetes: Minikube, Docker Desktop Kubernetes, or K3s
- Application: frontend + backend + database
- Containerization: Docker
- Deployment: Kubernetes manifests

### Background

Modern cloud applications are typically packaged as containers, deployed on Kubernetes, and configured through declarative manifests. This project requires building a small but complete cloud-native application and showing how it is deployed, configured, and exposed.

## 7. E1 Requirements

### Basic Requirements

Every group should complete the following:

- Implement a minimum working bookstore system with:
  - a frontend page
  - a backend API
  - a database
- Containerize the application with Docker.
- Deploy the system on Kubernetes using:
  - Deployment
  - Service
- Support at least two core bookstore features, such as:
  - browse or search books
  - shopping cart
  - place order

### Standard Requirements

For a strong project, the system should also include:

- Use ConfigMap and Secret appropriately.
- Expose the application through Ingress.
- Provide a clean architecture diagram.
- Demonstrate a complete deployment workflow.

### Advanced / Bonus Requirements

Optional improvements:

- Add auto-scaling.
- Add basic monitoring or dashboard support.
- Improve the database schema and API design.
- Conduct a small performance test.

## 8. Expected Engineering Focus

The project should clearly demonstrate:

- cloud-native application packaging
- Docker-based containerization
- Kubernetes deployment
- Kubernetes service exposure
- configuration management with ConfigMap and Secret
- end-to-end deployment and demo workflow

## 9. Suggested Acceptance Checklist

Before final submission, verify that:

- The frontend can be opened from the deployed environment.
- The backend API is reachable from the frontend.
- The database is used by the backend.
- At least two bookstore features work end to end.
- Docker images can be built successfully.
- Kubernetes manifests can deploy the system from a clean environment.
- Services expose the correct components.
- Ingress is configured and documented.
- ConfigMap and Secret are used for non-code configuration.
- README explains setup, deployment, testing, and reproduction steps.
- Report includes design, implementation, deployment, evaluation, limitations, and references.
- Demo video shows the deployed system and the main user flow.

## 10. Difficulty Level

E1 is classified as:

Level 2: Moderate-Challenging

This is suitable for a solid project with meaningful implementation and deployment work.

## 11. Grading Rubric for Engineering-Oriented Projects

- System design: 20%
- Implementation quality: 25%
- Deployment / demo: 20%
- Completeness and robustness: 20%
- Proposal / Presentation / Report / Demo: 15%

## 12. Milestones

### Milestone 1: Topic Selection

Due: April 19, 2026

Submission:

- short proposal, 1-2 pages

Weight:

- 20% of total project score

### Milestone 2: Progress Presentation / Demonstration

Date: May 7, 2026

Submission:

- progress presentation
- demo video or live demo, optional

Weight:

- 30% of total project score

### Milestone 3: Final Submission

Due: May 21, 2026

Submission:

- code and configuration files
- final report
- demo video

Weight:

- 50% of total project score

## 13. Project Deliverables Clarification

The instructor clarified that there is no strict report template, but the report and demo video should clearly show the project objective, design, implementation, deployment, and working behavior.

### Project Report

A good project report should generally include:

- project objective and motivation
- system architecture and overall design
- implementation and deployment details
- testing, evaluation, or experimental results
- challenges encountered and how they were addressed
- discussion and conclusion

For this engineering-oriented E1 project, the report should place more emphasis on:

- system design
- Kubernetes deployment
- robustness
- demonstration of functionality

### Demo Video

The demo video should mainly demonstrate the core workflow and key functionalities of the bookstore system.

The video may include:

- deployment and running services
- major bookstore features
- testing scenarios
- failure recovery or scaling behavior
- brief explanation of the architecture or request/dataflow

There is no strict time limit, but a concise and focused video of approximately 5-10 minutes is generally sufficient.

### Additional Notes

The project handout contains the main requirements. Additional clarifications may be provided later if necessary, but there will not be a highly rigid specification. Part of the project is intended to encourage design decisions and exploration.

## 14. Academic Integrity and AI Usage

AI tools such as ChatGPT, Claude, Copilot, or similar tools may be used for:

- brainstorming
- debugging
- explaining errors
- writing boilerplate code
- polishing documentation

However:

- All submitted work must be understood and verified by the team.
- Major AI usage should be disclosed in an appendix or short note.
- Blindly copying AI-generated code or text without verification is not acceptable.
- The project will be evaluated based on the team's understanding.

## 15. Final Submission Focus for This Repository

For this E1 bookstore project, the repository should make it easy to find:

- application source code
- Dockerfiles or image build instructions
- Kubernetes manifests
- ConfigMap and Secret definitions or templates
- Ingress configuration
- database initialization or schema files
- deployment scripts or commands
- README reproduction guide
- report PDF
- presentation slides
- demo video link or file
