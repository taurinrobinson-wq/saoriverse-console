"""
FirstPerson API Integration Hub
Image rendering, document generation, and external API management
"""

import base64
import io
from datetime import datetime
from typing import Any, Dict, List

import openai
import pandas as pd
import requests
import streamlit as st
from PIL import Image


class ImageGenerationAPI:
    """Handle image generation APIs"""

    def __init__(self):
        self.openai_client = None
        self.init_apis()

    def init_apis(self):
        """Initialize API clients"""
        try:
            # OpenAI API
            if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
                openai.api_key = st.secrets["openai"]["api_key"]
                self.openai_client = openai
        except Exception as e:
            st.warning(f"⚠️ API initialization warning: {e}")

    def generate_dalle_image(self, prompt: str, model: str = "dall-e-3", size: str = "1024x1024", quality: str = "standard") -> Dict[str, Any]:
        """Generate image using DALL-E"""
        try:
            if not self.openai_client:
                return {"success": False, "error": "OpenAI API not configured"}

            response = self.openai_client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )

            image_url = response.data[0].url
            revised_prompt = getattr(
                response.data[0], 'revised_prompt', prompt)

            return {
                "success": True,
                "image_url": image_url,
                "revised_prompt": revised_prompt,
                "model": model,
                "size": size,
                "quality": quality
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_stable_diffusion_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate image using Stability AI"""
        try:
            if "stability" not in st.secrets or "api_key" not in st.secrets["stability"]:
                return {"success": False, "error": "Stability AI API key not configured"}

            api_key = st.secrets["stability"]["api_key"]

            # Stability AI API call
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }

            data = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": kwargs.get("guidance_scale", 7.5),
                "steps": kwargs.get("steps", 50),
                "samples": 1,
                "width": kwargs.get("width", 1024),
                "height": kwargs.get("height", 1024),
            }

            response = requests.post(
                url, headers=headers, json=data, timeout=60)

            if response.status_code == 200:
                result = response.json()
                image_data = base64.b64decode(result["artifacts"][0]["base64"])

                return {
                    "success": True,
                    "image_data": image_data,
                    "prompt": prompt,
                    "model": "stable-diffusion-xl"
                }
            return {"success": False, "error": f"API error: {response.status_code}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_replicate_image(self, prompt: str, model: str = "controlnet") -> Dict[str, Any]:
        """Generate image using Replicate API"""
        try:
            if "replicate" not in st.secrets or "api_token" not in st.secrets["replicate"]:
                return {"success": False, "error": "Replicate API token not configured"}

            # This would integrate with Replicate's API
            # For now, returning placeholder
            return {
                "success": False,
                "error": "Replicate integration coming soon"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class DocumentGenerationAPI:
    """Handle document generation APIs"""

    def __init__(self):
        pass

    def generate_pdf_report(self, user_data: Dict[str, Any], template: str = "emotional_report") -> Dict[str, Any]:
        """Generate PDF report from user data"""
        try:
            # This would integrate with a PDF generation service
            # For now, creating a simple HTML-to-PDF concept

            html_content = self.create_html_report(user_data, template)

            # In production, this would call a PDF API like:
            # - PDFShift API
            # - Puppeteer/Playwright
            # - WeasyPrint

            return {
                "success": True,
                "html_content": html_content,
                "pdf_url": None,  # Would be actual PDF URL
                "template": template,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_html_report(self, user_data: Dict[str, Any], template: str) -> str:
        """Create HTML content for reports"""

        if template == "emotional_report":
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>FirstPerson Emotional Journey Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ text-align: center; border-bottom: 2px solid #2E2E2E; padding-bottom: 20px; }}
                    .section {{ margin: 30px 0; }}
                    .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; }}
                    .conversation {{ border-left: 4px solid #2E2E2E; padding-left: 15px; margin: 15px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>FP FirstPerson Emotional Journey Report</h1>
                    <p>Personal AI Companion Analysis</p>
                    <p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div class="section">
                    <h2>User Overview</h2>
                    <div class="metric">
                        <strong>Username:</strong> {user_data.get('username', 'N/A')}
                    </div>
                    <div class="metric">
                        <strong>Member Since:</strong> {user_data.get('created_at', 'N/A')}
                    </div>
                    <div class="metric">
                        <strong>Total Conversations:</strong> {len(user_data.get('conversations', []))}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Emotional Insights</h2>
                    <div class="metric">
                        <strong>Most Common Emotional Theme:</strong> Reflection & Growth
                    </div>
                    <div class="metric">
                        <strong>Processing Mode Preference:</strong> {user_data.get('preferred_mode', 'Hybrid')}
                    </div>
                    <div class="metric">
                        <strong>Average Response Satisfaction:</strong> High
                    </div>
                </div>
                
                <div class="section">
                    <h2>Recent Conversations</h2>
                    {''.join([f'<div class="conversation"><strong>Session:</strong> {conv.get("timestamp", "")[:10]}<br><strong>Mode:</strong> {conv.get("mode", "")}<br><strong>Processing Time:</strong> {conv.get("processing_time", "")}</div>' for conv in user_data.get('conversations', [])[-5:]])}
                </div>
            </body>
            </html>
            """

        return "<html><body><h1>Report template not found</h1></body></html>"

    def generate_docx_template(self, data: Dict[str, Any], template_type: str) -> Dict[str, Any]:
        """Generate DOCX document from template"""
        try:
            # This would integrate with python-docx and docxtpl
            # For now, returning placeholder

            return {
                "success": True,
                "template_type": template_type,
                "data_points": len(data),
                "generated_at": datetime.now().isoformat(),
                "note": "DOCX generation coming soon"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_excel_export(self, data: List[Dict[str, Any]], export_type: str) -> Dict[str, Any]:
        """Generate Excel file from data"""
        try:
            # Create DataFrame
            df = pd.DataFrame(data)

            # Create Excel file in memory
            excel_buffer = io.BytesIO()

            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=export_type, index=False)

                # Add metadata sheet
                metadata = pd.DataFrame({
                    'Property': ['Export Type', 'Generated At', 'Record Count', 'Generated By'],
                    'Value': [export_type, datetime.now().isoformat(), len(data), 'FirstPerson Admin']
                })
                metadata.to_excel(writer, sheet_name='Metadata', index=False)

            excel_data = excel_buffer.getvalue()

            return {
                "success": True,
                "excel_data": excel_data,
                "export_type": export_type,
                "record_count": len(data),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class APITestInterface:
    """Interface for testing API integrations"""

    def __init__(self):
        self.image_api = ImageGenerationAPI()
        self.doc_api = DocumentGenerationAPI()

    def render_image_testing(self):
        """Render image generation testing interface"""
        st.subheader("🖼️ Image Generation Testing")

        tab1, tab2, tab3 = st.tabs(["DALL-E", "Stable Diffusion", "Replicate"])

        with tab1:
            st.markdown("#### DALL-E Image Generation")

            col1, col2 = st.columns([2, 1])

            with col1:
                dalle_prompt = st.text_area(
                    "Image Prompt",
                    value="A serene digital artwork representing emotional healing and personal growth",
                    height=100,
                    help="Describe the image you want to generate"
                )

            with col2:
                dalle_model = st.selectbox("Model", ["dall-e-3", "dall-e-2"])
                dalle_size = st.selectbox(
                    "Size", ["1024x1024", "1792x1024", "1024x1792"])
                dalle_quality = st.selectbox("Quality", ["standard", "hd"])

            if st.button("🎨 Generate DALL-E Image", type="primary"):
                with st.spinner("Generating image..."):
                    result = self.image_api.generate_dalle_image(
                        dalle_prompt, dalle_model, dalle_size, dalle_quality
                    )

                if result["success"]:
                    st.success("✅ Image generated successfully!")

                    # Display image
                    try:
                        st.image(result["image_url"],
                                 caption="Generated Image")

                        # Show details
                        with st.expander("Generation Details"):
                            st.json(result)

                    except Exception as e:
                        st.error(f"Error displaying image: {e}")
                        st.json(result)
                else:
                    st.error(f"❌ Generation failed: {result['error']}")

        with tab2:
            st.markdown("#### Stable Diffusion Generation")

            sd_prompt = st.text_area(
                "Stable Diffusion Prompt",
                value="Emotional journey visualization, digital art, peaceful, growth",
                height=80
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                sd_steps = st.slider("Steps", 10, 150, 50)
            with col2:
                sd_guidance = st.slider("Guidance Scale", 1.0, 20.0, 7.5, 0.5)
            with col3:
                sd_width = st.selectbox("Width", [512, 768, 1024], index=2)
                sd_height = st.selectbox("Height", [512, 768, 1024], index=2)

            if st.button("🎨 Generate Stable Diffusion Image"):
                with st.spinner("Generating with Stable Diffusion..."):
                    result = self.image_api.generate_stable_diffusion_image(
                        sd_prompt,
                        steps=sd_steps,
                        guidance_scale=sd_guidance,
                        width=sd_width,
                        height=sd_height
                    )

                if result["success"]:
                    st.success("✅ Image generated!")

                    # Display image from binary data
                    image = Image.open(io.BytesIO(result["image_data"]))
                    st.image(image, caption="Stable Diffusion Generated Image")

                    with st.expander("Generation Details"):
                        st.json({k: v for k, v in result.items()
                                if k != "image_data"})
                else:
                    st.error(f"❌ Generation failed: {result['error']}")

        with tab3:
            st.markdown("#### Replicate API Testing")
            st.info("🚧 Replicate integration coming soon!")

            replicate_models = st.multiselect(  # noqa: F841  # used for UI selection side-effect
                "Available Models",
                ["ControlNet", "Real-ESRGAN", "Sketch-to-Image", "Style Transfer"],
                help="Models available through Replicate API"
            )

            if st.button("Test Replicate Connection"):
                st.warning("⚠️ Integration in development")

    def render_document_testing(self):
        """Render document generation testing interface"""
        st.subheader("📄 Document Generation Testing")

        tab1, tab2, tab3 = st.tabs(
            ["PDF Reports", "DOCX Templates", "Excel Export"])

        with tab1:
            st.markdown("#### PDF Report Generation")

            template_type = st.selectbox(
                "Report Template",
                ["emotional_report", "glyph_analysis", "user_summary"],
                help="Select report template type"
            )

            # Mock user data for testing
            mock_user_data = {
                "username": "test_user",
                "created_at": "2025-10-01",
                "conversations": [
                    {"timestamp": "2025-10-15T10:30:00",
                        "mode": "hybrid", "processing_time": "2.3s"},
                    {"timestamp": "2025-10-15T14:20:00",
                        "mode": "ai_preferred", "processing_time": "1.8s"},
                    {"timestamp": "2025-10-15T18:45:00",
                        "mode": "hybrid", "processing_time": "2.1s"}
                ],
                "preferred_mode": "hybrid"
            }

            if st.button("📊 Generate PDF Report", type="primary"):
                with st.spinner("Generating PDF report..."):
                    result = self.doc_api.generate_pdf_report(
                        mock_user_data, template_type)

                if result["success"]:
                    st.success("✅ Report generated!")

                    # Show HTML preview
                    with st.expander("📄 HTML Preview"):
                        # Display HTML content as text for now
                        st.code(result["html_content"], language="html")

                    with st.expander("Generation Details"):
                        st.json({k: v for k, v in result.items()
                                if k != "html_content"})

                    st.info("🔧 PDF conversion integration coming soon!")
                else:
                    st.error(f"❌ Generation failed: {result['error']}")

        with tab2:
            st.markdown("#### DOCX Template Generation")

            template_format = st.selectbox(
                "Document Format",
                ["Emotional Report", "Glyph Analysis",
                    "User Summary", "Progress Report"]
            )

            if st.button("📝 Generate DOCX Document"):
                result = self.doc_api.generate_docx_template(
                    {}, template_format)
                st.json(result)
                st.info("🔧 DOCX template integration coming soon!")

        with tab3:
            st.markdown("#### Excel Export Generation")

            export_format = st.selectbox(
                "Export Type",
                ["User Analytics", "Glyph Matrices",
                    "Conversation Logs", "System Reports"]
            )

            # Mock data for Excel export
            mock_excel_data = [
                {"user": "john_doe", "conversations": 23,
                    "avg_response_time": 2.1, "preferred_mode": "hybrid"},
                {"user": "jane_smith", "conversations": 8,
                    "avg_response_time": 1.9, "preferred_mode": "ai_preferred"},
                {"user": "test_user", "conversations": 45,
                    "avg_response_time": 2.3, "preferred_mode": "hybrid"}
            ]

            if st.button("📊 Generate Excel Export", type="primary"):
                with st.spinner("Creating Excel file..."):
                    result = self.doc_api.generate_excel_export(
                        mock_excel_data, export_format)

                if result["success"]:
                    st.success("✅ Excel file generated!")

                    # Offer download
                    st.download_button(
                        label="📥 Download Excel File",
                        data=result["excel_data"],
                        file_name=f"{export_format}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    with st.expander("Export Details"):
                        st.json({k: v for k, v in result.items()
                                if k != "excel_data"})
                else:
                    st.error(f"❌ Export failed: {result['error']}")


def main():
    """Main API testing interface"""

    st.set_page_config(
        page_title="FirstPerson API Testing",
        page_icon="🔌",
        layout="wide"
    )

    # Header
    col1, col2 = st.columns([1, 6])
    with col1:
        try:
            st.image("/static/graphics/FirstPerson-Logo-normalized.svg", width=40)
        except Exception:
            st.markdown("🔌")
    with col2:
        st.markdown("# FirstPerson API Integration Hub")
        st.markdown("*Test and configure external API integrations*")

    # API Testing Interface
    api_tester = APITestInterface()

    tab1, tab2, tab3 = st.tabs(
        ["🖼️ Image APIs", "📄 Document APIs", "⚙️ Configuration"])

    with tab1:
        api_tester.render_image_testing()

    with tab2:
        api_tester.render_document_testing()

    with tab3:
        st.subheader("🔧 API Configuration")

        st.markdown("### API Key Management")
        st.info("🔐 API keys are managed through Streamlit secrets")

        # Configuration status
        config_status = {
            "OpenAI API": "openai" in st.secrets and "api_key" in st.secrets.get("openai", {}),
            "Stability AI": "stability" in st.secrets and "api_key" in st.secrets.get("stability", {}),
            "Replicate": "replicate" in st.secrets and "api_token" in st.secrets.get("replicate", {}),
        }

        for service, configured in config_status.items():
            status_emoji = "🟢" if configured else "🔴"
            status_text = "Configured" if configured else "Not Configured"
            st.write(f"{status_emoji} **{service}**: {status_text}")

        st.markdown("### Required Secrets Configuration")
        st.code("""
# Add to .streamlit/secrets.toml
[openai]
api_key = "your-openai-api-key"

[stability]
api_key = "your-stability-ai-key"

[replicate]
api_token = "your-replicate-token"
        """, language="toml")


if __name__ == "__main__":
    main()
