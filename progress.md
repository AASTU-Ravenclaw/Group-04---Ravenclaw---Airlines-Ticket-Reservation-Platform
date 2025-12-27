# Progress Log

## Week 7 – System Design (Phase 1, Part 1)  

### Summary of Work Completed
- Completed high-level system architecture for the project.
- Designed component and deployment diagrams using draw.io/PlantUML.
- Finalized list of microservices and their boundaries.
- Defined communication patterns:  
  - REST/gRPC for synchronous interactions  
  - RabbitMQ/Kafka/Redis for Pub/Sub messaging  
- Defined preliminary Pub/Sub event schemas.
- Started drafting the System Design Document (SDD).

### Issues / Blockers
- No issues reported.

### Planned Work for Next Week
- Complete the full System Design Document (SDD).
- Finalize all API schemas.
- Finalize Pub/Sub event schemas.
- Prepare the Week 8 architecture submission package.

---

## Week 8 – System Design Completion (Phase 1, Part 2)  

### Summary of Work Completed
- Finalized the complete System Design Document (SDD).
- Finalized detailed API contracts for all services.
- Created message flow diagrams to illustrate service interactions and event propagation.
- Completed the database schema and overall data model.
- Prepared and submitted the full Week 8 Architecture Design Milestone deliverable.

### Commits / PRs
- Uploaded final SDD (PDF/Markdown).
- Uploaded openapi.yaml.


### Issues / Blockers
- None — all Week 8 tasks completed successfully.

### Planned Work for Next Week
- Begin Phase 2 implementation (Week 9–11).
- Set up service scaffolding for each microservice.
- Initialize message broker configuration and Pub/Sub topics.
- Implement initial endpoints and service bootstrapping.


## Week 9 – Phase 2 Implementation (Service Development)

### Summary of Work Completed
During Week 9, the team began transitioning from design activities into hands-on implementation. The full backend repository structure for the microservices was created and pushed, including directories for service modules, configurations, shared utilities, message-broker setup, and initial API routing.  
Although most of the actual service logic is still under development, the foundational scaffolding for each microservice is now in place, allowing us to begin implementing the core functionalities defined in the SDD and OpenAPI specifications.  
This week’s primary focus was ensuring that the project structure is clean, scalable, and aligned with the architectural guidelines established in Weeks 7–8. 
Overall, Week 9 sets the groundwork for the full service implementation that will follow.

### Commits / PRs
- Pushed full backend repository structure.
- Added initial folders for services, shared modules, and message-broker configuration.

### Issues / Blockers
- No major blockers.

### Planned Work for Next Week
- Complete implementation of core service logic for all microservices.
- Finalize integration of REST/gRPC communication and Pub/Sub event publishing.
- Begin writing unit tests for implemented features.
- Prepare for mid-Phase 2 validation and internal testing.

## Week 10 – Phase 2 Implementation

### Summary of Work Completed
During Week 10, the team continued building on the work started last week. The basic structure for all microservices is now working, and the main focus was adding simple, working features to each service. 

Key work done:
- Added basic logic to the main microservices.
- Connected REST/gRPC endpoints to simple controllers.
- Set up the message broker (RabbitMQ/Kafka/Redis) and tested basic publishing and subscribing.
- Improved shared configuration for environment variables and service connections.

### Commits / PRs
- Added basic service logic.
- Added message broker setup and sample events.
- Updated Docker Compose to run all services.

### Issues / Blockers
- No major blockers.

### Planned Work for Next Week
- Finish the remaining service logic and endpoints.
- Complete event publishing and subscribing flow.
- Start writing unit tests.
- Begin integration testing across services.
- Update documentation for APIs and event schemas.