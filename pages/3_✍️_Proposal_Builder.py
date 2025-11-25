"""
Proposal Builder Page - AI-assisted grant proposal generation
"""
import streamlit as st
import sys
import os
import time

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Page configuration
st.set_page_config(
    page_title="Proposal Builder | Grant Seeker's Co-Pilot",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        
        .builder-header {
            background-color: #eef6ff;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .section-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .section-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2d3748;
        }
        
        .ai-badge {
            background-color: #805ad5;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
        }
        
        .template-card {
            background-color: #f7fafc;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .template-card:hover {
            border-color: #3182ce;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .template-selected {
            border-color: #3182ce;
            background-color: #ebf8ff;
        }
        
        .progress-step {
            display: flex;
            align-items: center;
            padding: 0.5rem 0;
        }
        
        .progress-dot {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 0.75rem;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .progress-dot-complete {
            background-color: #38a169;
            color: white;
        }
        
        .progress-dot-current {
            background-color: #3182ce;
            color: white;
        }
        
        .progress-dot-pending {
            background-color: #e2e8f0;
            color: #718096;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'proposal_sections' not in st.session_state:
    st.session_state.proposal_sections = {
        'executive_summary': '',
        'statement_of_need': '',
        'goals_objectives': '',
        'methods': '',
        'budget_narrative': '',
        'evaluation': ''
    }

if 'org_profile' not in st.session_state:
    st.session_state.org_profile = {
        'org_name': '',
        'mission': '',
        'contact_name': '',
        'contact_email': '',
        'budget_summary': ''
    }

if 'proposal_drafts' not in st.session_state:
    st.session_state.proposal_drafts = []

# Sample generated content templates
SAMPLE_CONTENT = {
    'executive_summary': """The [Organization Name] respectfully requests $[Amount] to support our [Project Name] initiative. This comprehensive program will serve [Number] community members over [Duration], addressing critical needs in [Focus Area].

Our organization has a proven track record of [Achievement], having served over [Number] individuals since [Year]. This project aligns directly with [Funder Name]'s mission to [Funder Mission].

Key outcomes include:
• [Outcome 1]
• [Outcome 2]
• [Outcome 3]

With your support, we will create lasting impact in our community while advancing sustainable solutions for [Problem].""",
    
    'statement_of_need': """[Community/Region] faces significant challenges in [Problem Area]. According to recent data from [Source], [Statistic] of residents are affected by [Issue].

The need for intervention is urgent:
• [Data Point 1]: [Supporting statistic]
• [Data Point 2]: [Supporting statistic]
• [Data Point 3]: [Supporting statistic]

Current resources are insufficient to address this growing need. [Gap in Services] leaves many community members without access to [Essential Service/Resource].

Our target population of [Description] has been disproportionately impacted by [Factor]. Through direct engagement with community members, we have identified [Specific Need] as the most pressing priority.""",
    
    'goals_objectives': """Goal 1: [Broad Goal Statement]
• Objective 1.1: By [Date], [Measurable Outcome]
• Objective 1.2: By [Date], [Measurable Outcome]

Goal 2: [Broad Goal Statement]
• Objective 2.1: By [Date], [Measurable Outcome]
• Objective 2.2: By [Date], [Measurable Outcome]

Goal 3: [Broad Goal Statement]
• Objective 3.1: By [Date], [Measurable Outcome]
• Objective 3.2: By [Date], [Measurable Outcome]

Each objective includes specific, measurable indicators that will allow us to track progress and demonstrate impact to stakeholders.""",
    
    'methods': """Our implementation strategy follows a phased approach:

Phase 1: [Month 1-3] - Planning and Preparation
• [Activity 1]
• [Activity 2]
• [Activity 3]

Phase 2: [Month 4-9] - Implementation
• [Activity 1]
• [Activity 2]
• [Activity 3]

Phase 3: [Month 10-12] - Evaluation and Sustainability
• [Activity 1]
• [Activity 2]
• [Activity 3]

Key personnel include:
• [Role 1]: [Responsibilities]
• [Role 2]: [Responsibilities]
• [Role 3]: [Responsibilities]

We will partner with [Partner Organization] to leverage their expertise in [Area].""",
    
    'budget_narrative': """Total Project Budget: $[Amount]

Personnel (60%): $[Amount]
• Project Director (0.5 FTE): $[Amount]
• Program Coordinator (1.0 FTE): $[Amount]
• Support Staff (0.25 FTE): $[Amount]

Program Expenses (25%): $[Amount]
• Materials and supplies: $[Amount]
• Equipment: $[Amount]
• Participant support: $[Amount]

Administrative Costs (15%): $[Amount]
• Indirect costs (10%): $[Amount]
• Evaluation: $[Amount]

Cost-effectiveness: This budget represents a cost of $[Amount] per participant served, which compares favorably to similar programs in our region.""",
    
    'evaluation': """Our evaluation plan employs a mixed-methods approach to measure both process and outcomes.

Process Evaluation:
• Monthly tracking of participation rates and demographics
• Quarterly satisfaction surveys
• Staff observations and documentation

Outcome Evaluation:
• Pre/post assessments for all participants
• Follow-up surveys at 6 and 12 months
• Focus groups with program completers

Key Performance Indicators:
1. [KPI 1]: Target [X]%, measured by [Method]
2. [KPI 2]: Target [X]%, measured by [Method]
3. [KPI 3]: Target [X]%, measured by [Method]

Data will be collected using [Tool/System] and analyzed by [Staff/Consultant]. Results will be shared with stakeholders through [Report Format]."""
}


def generate_section(section_name, project_details, grant_info, tone="formal"):
    """Simulate AI generation of a proposal section."""
    # In production, this would call the Writer Agent
    return SAMPLE_CONTENT.get(section_name, "Content generation in progress...")


def main():
    """Main function for the Proposal Builder page."""
    
    # Get selected grant from session state
    grant = st.session_state.get('selected_grant', {
        "title": "Community Garden Initiative Grant",
        "funder": "Green Earth Foundation",
        "deadline": "2025-03-15",
        "amount": "$10,000 - $50,000"
    })
    
    # Header
    st.markdown(f"""
        <div class="builder-header">
            <h2>✍️ Proposal Builder</h2>
            <p style="color: #4a5568;">Building proposal for: <strong>{grant.get('title', 'New Proposal')}</strong></p>
            <p style="color: #718096; font-size: 0.9rem;">🏛️ {grant.get('funder', 'Unknown Funder')} | 📅 Deadline: {grant.get('deadline', 'TBD')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Main layout with sidebar controls
    col_main, col_sidebar = st.columns([3, 1])
    
    with col_sidebar:
        st.markdown("### ⚙️ AI Settings")
        
        # Template selector
        template = st.selectbox(
            "Template Style",
            ["Standard", "Brief", "Detailed"],
            help="Choose the level of detail for generated content"
        )
        
        # Tone selector
        tone = st.selectbox(
            "Tone",
            ["Formal", "Persuasive", "Concise"],
            help="Select the writing tone"
        )
        
        # Style toggles
        st.markdown("### 📝 Style Options")
        use_data = st.checkbox("Include statistics", value=True)
        use_quotes = st.checkbox("Include testimonials", value=False)
        use_visuals = st.checkbox("Suggest visual elements", value=True)
        
        st.markdown("---")
        
        # Progress tracking
        st.markdown("### 📊 Progress")
        sections_complete = sum(1 for v in st.session_state.proposal_sections.values() if v)
        total_sections = len(st.session_state.proposal_sections)
        
        st.progress(sections_complete / total_sections)
        st.caption(f"{sections_complete}/{total_sections} sections complete")
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### 🚀 Quick Actions")
        
        if st.button("🔄 Regenerate All", use_container_width=True):
            with st.spinner("Regenerating all sections..."):
                time.sleep(3)
                for key in st.session_state.proposal_sections:
                    st.session_state.proposal_sections[key] = generate_section(key, "", "", tone.lower())
                st.success("All sections regenerated!")
                st.rerun()
        
        if st.button("💾 Save Draft", use_container_width=True):
            draft = {
                'timestamp': time.strftime("%Y-%m-%d %H:%M"),
                'grant': grant.get('title', 'Untitled'),
                'sections': st.session_state.proposal_sections.copy()
            }
            st.session_state.proposal_drafts.append(draft)
            st.success("Draft saved!")
        
        if st.button("📄 Export PDF", use_container_width=True):
            st.info("PDF export feature coming soon!")
        
        if st.button("📝 Export DOCX", use_container_width=True):
            st.info("DOCX export feature coming soon!")
    
    with col_main:
        # Organization Profile Section
        with st.expander("📋 Organization Profile", expanded=False):
            st.markdown("*Fill in your organization details to personalize the proposal*")
            
            profile_col1, profile_col2 = st.columns(2)
            
            with profile_col1:
                st.session_state.org_profile['org_name'] = st.text_input(
                    "Organization Name",
                    value=st.session_state.org_profile.get('org_name', ''),
                    placeholder="Your Organization Name"
                )
                
                st.session_state.org_profile['contact_name'] = st.text_input(
                    "Contact Name",
                    value=st.session_state.org_profile.get('contact_name', ''),
                    placeholder="Primary Contact"
                )
            
            with profile_col2:
                st.session_state.org_profile['contact_email'] = st.text_input(
                    "Contact Email",
                    value=st.session_state.org_profile.get('contact_email', ''),
                    placeholder="email@organization.org"
                )
                
                st.session_state.org_profile['budget_summary'] = st.text_input(
                    "Annual Budget",
                    value=st.session_state.org_profile.get('budget_summary', ''),
                    placeholder="e.g., $500,000"
                )
            
            st.session_state.org_profile['mission'] = st.text_area(
                "Mission Statement",
                value=st.session_state.org_profile.get('mission', ''),
                placeholder="Describe your organization's mission...",
                height=100
            )
        
        st.markdown("---")
        
        # Proposal Sections
        st.markdown("### 📑 Proposal Sections")
        
        sections = [
            ("executive_summary", "Executive Summary", "A concise overview of your proposal"),
            ("statement_of_need", "Statement of Need", "Why this project is necessary"),
            ("goals_objectives", "Goals & Objectives", "What you aim to achieve"),
            ("methods", "Methods & Approach", "How you will implement the project"),
            ("budget_narrative", "Budget Narrative", "Justification for your budget"),
            ("evaluation", "Evaluation Plan", "How you will measure success")
        ]
        
        for section_key, section_title, section_desc in sections:
            with st.container():
                st.markdown(f"""
                    <div class="section-header">
                        <span class="section-title">{section_title}</span>
                        <span class="ai-badge">AI Assisted</span>
                    </div>
                """, unsafe_allow_html=True)
                
                st.caption(section_desc)
                
                # Text area for the section
                current_content = st.session_state.proposal_sections.get(section_key, '')
                
                new_content = st.text_area(
                    f"{section_title} Content",
                    value=current_content,
                    height=200,
                    key=f"textarea_{section_key}",
                    label_visibility="collapsed",
                    placeholder=f"Enter your {section_title.lower()} here or click 'Generate' to create AI content..."
                )
                
                # Update session state if content changed
                if new_content != current_content:
                    st.session_state.proposal_sections[section_key] = new_content
                
                # Action buttons for each section
                btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
                
                with btn_col1:
                    if st.button("✨ Generate", key=f"gen_{section_key}", use_container_width=True):
                        with st.spinner("Generating content..."):
                            time.sleep(1.5)
                            generated = generate_section(section_key, "", "", tone.lower())
                            st.session_state.proposal_sections[section_key] = generated
                            st.rerun()
                
                with btn_col2:
                    if st.button("📝 Expand", key=f"expand_{section_key}", use_container_width=True):
                        if st.session_state.proposal_sections[section_key]:
                            st.info("Expansion feature: AI will add more detail to this section")
                        else:
                            st.warning("Please generate content first")
                
                with btn_col3:
                    if st.button("✂️ Shorten", key=f"short_{section_key}", use_container_width=True):
                        if st.session_state.proposal_sections[section_key]:
                            st.info("Shortening feature: AI will condense this section")
                        else:
                            st.warning("Please generate content first")
                
                with btn_col4:
                    if st.button("🔧 Improve", key=f"improve_{section_key}", use_container_width=True):
                        if st.session_state.proposal_sections[section_key]:
                            st.info("Improvement feature: AI will enhance grammar and clarity")
                        else:
                            st.warning("Please generate content first")
                
                st.markdown("---")
        
        # Revision History
        with st.expander("📜 Revision History", expanded=False):
            if st.session_state.proposal_drafts:
                for i, draft in enumerate(reversed(st.session_state.proposal_drafts)):
                    st.markdown(f"**Draft {len(st.session_state.proposal_drafts) - i}** - {draft['timestamp']}")
                    st.caption(f"Grant: {draft['grant']}")
                    if st.button("Restore", key=f"restore_{i}"):
                        st.session_state.proposal_sections = draft['sections'].copy()
                        st.success("Draft restored!")
                        st.rerun()
                    st.markdown("---")
            else:
                st.caption("No saved drafts yet. Click 'Save Draft' to save your progress.")


if __name__ == "__main__":
    main()
