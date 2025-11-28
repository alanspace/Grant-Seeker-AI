# # # from diagrams import Diagram, Cluster, Edge
# # # from diagrams.onprem.client import User
# # # from diagrams.programming.language import Python
# # # from diagrams.onprem.database import Cassandra # Representing Cache/Storage
# # # from diagrams.gcp.ml import VertexAI
# # # from diagrams.saas.chat import Slack # Using generic icon for External API
# # # from diagrams.custom import Custom
# # # from diagrams.onprem.network import Internet
# # # from diagrams.programming.flowchart import Document

# # # # Graph attributes for a professional look
# # # graph_attr = {
# # #     "fontsize": "20",
# # #     "bgcolor": "white",
# # #     "pad": "0.5"
# # # }

# # # with Diagram("Grant Seeker Agent Architecture", show=False, direction="LR", graph_attr=graph_attr):
    
# # #     user = User("User Query")
    
# # #     with Cluster("Local Execution Environment"):
# # #         orchestrator = Python("Orchestrator\n(GrantSeekerWorkflow)")
        
# # #         with Cluster("Session & Memory"):
# # #             cache = Cassandra("Local Cache\n(.cache/)")
# # #             # Using Document to represent session state in memory
# # #             session = Document("Session State\n(ADK)")

# # #         with Cluster("Agentic Layer"):
# # #             # Phase 1 Agent
# # #             finder = Python("GrantFinder Agent\n(The Scout)")
# # #             # Phase 2 Agent
# # #             extractor = Python("GrantExtractor Agent\n(The Analyst)")
            
# # #         output_file = Document("grants_output.json")

# # #     with Cluster("External Services"):
# # #         # Using Internet icon for Tavily Search/Scrape
# # #         tavily = Internet("Tavily API\n(Search & Extract)")
        
# # #         # Google Gemini
# # #         gemini = VertexAI("Google Gemini\n(Flash Model)")

# # #     # --- Data Flow ---

# # #     # 1. Initialization & Search
# # #     user >> Edge(label="1. Query") >> orchestrator
# # #     orchestrator >> Edge(style="dashed") >> cache
# # #     orchestrator >> Edge(label="2. Search Web") >> tavily
    
# # #     # 2. Phase 1: Discovery
# # #     tavily >> Edge(label="Raw Results") >> orchestrator
# # #     orchestrator >> Edge(label="3. Filter Results") >> finder
# # #     finder >> Edge(label="Reasoning") >> gemini
    
# # #     # 3. Phase 2: Parallel Extraction
# # #     orchestrator >> Edge(label="4. Scrape Content\n(Parallel)") >> tavily
# # #     tavily >> Edge(label="Page Content") >> orchestrator
# # #     orchestrator >> Edge(label="5. Extract Data") >> extractor
# # #     extractor >> Edge(label="Reasoning &\nValidation") >> gemini
    
# # #     # 4. Output
# # #     orchestrator >> Edge(label="6. Save JSON") >> output_file

# # # print("Diagram generated: grant_seeker_architecture.png")


# # from diagrams import Diagram, Cluster, Edge
# # from diagrams.onprem.client import User
# # from diagrams.programming.language import Python
# # from diagrams.onprem.database import Cassandra  # Cache
# # from diagrams.gcp.ml import VertexAI
# # from diagrams.onprem.network import Internet
# # from diagrams.programming.flowchart import Document

# # # Graph attributes for a vertical flow
# # graph_attr = {
# #     "fontsize": "22",
# #     "bgcolor": "white",
# #     "pad": "0.5",
# #     "splines": "ortho", # Makes lines straight/orthogonal for a cleaner look
# #     "nodesep": "0.6",   # Increase separation between nodes
# #     "ranksep": "0.8"    # Increase separation between layers
# # }

# # with Diagram("Grant Seeker Sequential Workflow", show=False, direction="TB", graph_attr=graph_attr):
    
# #     # --- Top Layer: Input ---
# #     user = User("User Query\n(Search Terms)")

# #     # --- Second Layer: Core Controller ---
# #     with Cluster("Controller Layer"):
# #         orchestrator = Python("Orchestrator\n(GrantSeekerWorkflow)")
# #         cache = Cassandra("Local Cache\n(.cache/)")
    
# #     # --- Third Layer: Phase 1 (Discovery) ---
# #     with Cluster("Phase 1: Discovery (The Scout)"):
# #         # Using Internet icon to represent the Search Action specifically
# #         search_api = Internet("Tavily Search API")
# #         finder_agent = Python("GrantFinder Agent")
# #         gemini_1 = VertexAI("Gemini Flash\n(Filtering)")
        
# #         # Invisible edge to force layout
# #         search_api - Edge(style="invis") - finder_agent

# #     # --- Fourth Layer: Phase 2 (Extraction) ---
# #     with Cluster("Phase 2: Extraction (The Analyst)"):
# #         # Using Internet icon to represent the Scrape Action specifically
# #         scrape_api = Internet("Tavily Extract API")
# #         extractor_agent = Python("GrantExtractor Agent\n(Parallel)")
# #         gemini_2 = VertexAI("Gemini Flash\n(Parsing)")

# #     # --- Bottom Layer: Output ---
# #     results = Document("grants_output.json")

# #     # ==========================================
# #     # DEFINING THE FLOW
# #     # ==========================================

# #     # 1. User starts the process
# #     user >> Edge(label="1. Input", color="black") >> orchestrator
    
# #     # 2. Orchestrator checks cache
# #     orchestrator >> Edge(label="2. Check/Store", style="dashed", color="gray") >> cache
    
# #     # 3. Phase 1 Execution
# #     orchestrator >> Edge(label="3. Query", color="blue") >> search_api
# #     search_api >> Edge(label="Raw Results", color="blue") >> finder_agent
# #     finder_agent >> Edge(label="Analyze", color="blue") >> gemini_1
    
# #     # 4. Transition to Phase 2
# #     # We connect the Agent from Phase 1 to the Orchestrator logic for Phase 2
# #     finder_agent >> Edge(label="4. Promising Leads", style="bold", color="black") >> orchestrator
    
# #     # 5. Phase 2 Execution
# #     orchestrator >> Edge(label="5. Scrape URL", color="green") >> scrape_api
# #     scrape_api >> Edge(label="HTML/Text", color="green") >> extractor_agent
# #     extractor_agent >> Edge(label="Extract Fields", color="green") >> gemini_2
    
# #     # 6. Final Output
# #     extractor_agent >> Edge(label="6. Structured Data", style="bold", color="black") >> results

# # print("Diagram generated: grant_seeker_sequential_workflow.png")


# from diagrams import Diagram, Cluster, Edge
# from diagrams.onprem.client import User
# from diagrams.programming.language import Python
# from diagrams.onprem.database import Cassandra
# from diagrams.gcp.ml import VertexAI
# from diagrams.onprem.network import Internet
# from diagrams.programming.flowchart import Document

# # Graph attributes for a wide, landscape view
# graph_attr = {
#     "fontsize": "20",
#     "bgcolor": "white",
#     "pad": "0.5",
#     "splines": "ortho",  # Orthogonal (straight) lines
#     "nodesep": "0.5",    # Horizontal separation
#     "ranksep": "1.0",    # Vertical separation between groups
#     "labelloc": "t"      # Label at the top
# }

# with Diagram("Grant Seeker Horizontal Pipeline", show=False, direction="LR", graph_attr=graph_attr):
    
#     # --- Far Left: Input ---
#     user = User("User Query")

#     # --- Control Center ---
#     with Cluster("Orchestration Layer"):
#         orchestrator = Python("Workflow\nManager")
#         cache = Cassandra("Local\nCache")
        
#     # --- Middle Left: Phase 1 ---
#     with Cluster("Phase 1: Discovery"):
#         search_api = Internet("Tavily\nSearch")
#         finder_agent = Python("GrantFinder\nAgent")
#         gemini_1 = VertexAI("Gemini\nReasoning")

#     # --- Middle Right: Phase 2 ---
#     with Cluster("Phase 2: Extraction"):
#         scrape_api = Internet("Tavily\nExtract")
#         extractor_agent = Python("GrantExtractor\nAgent")
#         gemini_2 = VertexAI("Gemini\nParsing")

#     # --- Far Right: Output ---
#     results = Document("Output\nJSON")

#     # ==========================================
#     # DEFINING THE FLOW (Left -> Right)
#     # ==========================================

#     # 1. Input processing
#     user >> Edge(label="Start") >> orchestrator
#     orchestrator - Edge(style="dashed") - cache # Bi-directional check

#     # 2. Phase 1 Flow
#     orchestrator >> Edge(label="Query") >> search_api
#     search_api >> Edge(label="Results") >> finder_agent
#     finder_agent >> Edge(label="Analyze") >> gemini_1
    
#     # 3. Transition (The "Handoff")
#     # Connecting Phase 1 Agent to Phase 2 Tools visually implies the pipeline flow
#     gemini_1 >> Edge(label="Promising Leads", style="bold", color="blue") >> scrape_api

#     # 4. Phase 2 Flow
#     scrape_api >> Edge(label="Content") >> extractor_agent
#     extractor_agent >> Edge(label="Extract") >> gemini_2

#     # 5. Final Output
#     gemini_2 >> Edge(label="Structured Data", style="bold", color="green") >> results

# print("Diagram generated: grant_seeker_horizontal_pipeline.png")


from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.programming.language import Python
from diagrams.onprem.database import Cassandra
from diagrams.gcp.ml import VertexAI
from diagrams.onprem.network import Internet
from diagrams.programming.flowchart import Document

# Graph attributes for a wide, landscape view
graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",  # Orthogonal (straight) lines
    "nodesep": "0.5",    # Horizontal separation
    "ranksep": "1.0",    # Vertical separation between groups
    "labelloc": "t"      # Label at the top
}

with Diagram("Grant Seeker Horizontal Pipeline", show=False, direction="LR", graph_attr=graph_attr):
    
    # --- Far Left: Input ---
    user = User("User Query")

    # --- Control Center ---
    with Cluster("Orchestration Layer"):
        orchestrator = Python("Workflow\nManager")
        cache = Cassandra("Local\nCache")
        
    # --- Middle Left: Phase 1 ---
    with Cluster("Phase 1: Discovery"):
        search_api = Internet("Tavily\nSearch")
        finder_agent = Python("GrantFinder\nAgent")
        gemini_1 = VertexAI("Gemini\nReasoning")

    # --- Middle Right: Phase 2 ---
    with Cluster("Phase 2: Extraction"):
        scrape_api = Internet("Tavily\nExtract")
        extractor_agent = Python("GrantExtractor\nAgent")
        gemini_2 = VertexAI("Gemini\nParsing")

    # --- Far Right: Output ---
    results = Document("Output\nJSON")

    # ==========================================
    # DEFINING THE FLOW (Left -> Right)
    # ==========================================

    # 1. Input processing
    user >> Edge(label="Start") >> orchestrator
    orchestrator - Edge(style="dashed") - cache # Bi-directional check

    # 2. Phase 1 Flow
    orchestrator >> Edge(label="Query") >> search_api
    search_api >> Edge(label="Results") >> finder_agent
    finder_agent >> Edge(label="Analyze") >> gemini_1
    
    # 3. Transition (The "Handoff")
    # Connecting Phase 1 Agent to Phase 2 Tools visually implies the pipeline flow
    gemini_1 >> Edge(label="Promising Leads", style="bold", color="blue") >> scrape_api

    # 4. Phase 2 Flow
    scrape_api >> Edge(label="Content") >> extractor_agent
    extractor_agent >> Edge(label="Extract") >> gemini_2

    # 5. Final Output
    gemini_2 >> Edge(label="Structured Data", style="bold", color="green") >> results

print("Diagram generated: grant_seeker_horizontal_pipeline.png")