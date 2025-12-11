import streamlit as st
import cv2
import pytesseract
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import time

# Page configuration
st.set_page_config(
    page_title="OCR Text Scanner",
    page_icon="📸",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .stButton > button {
        width: 100%;
    }
    canvas {
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'original_image' not in st.session_state:
    st.session_state.original_image = None
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'cropped_image' not in st.session_state:
    st.session_state.cropped_image = None
if 'canvas_key' not in st.session_state:
    st.session_state.canvas_key = 0
if 'last_file_id' not in st.session_state:
    st.session_state.last_file_id = None
if 'canvas_data' not in st.session_state:
    st.session_state.canvas_data = None
if 'input_method' not in st.session_state:
    st.session_state.input_method = "Upload"


def reset_state():
    """Reset all state except the original image"""
    st.session_state.cropped_image = None
    st.session_state.extracted_text = ""
    st.session_state.canvas_data = None
    st.session_state.canvas_key += 1


def preprocess_image(image):
    """Preprocesses the image to enhance text recognition."""
    if isinstance(image, Image.Image):
        image = np.array(image)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def extract_text_from_image(image):
    """Extracts text from the image using OCR."""
    processed_image = preprocess_image(image)
    return pytesseract.image_to_string(processed_image, config="--psm 6")


def get_roi_from_canvas(canvas_json, original_image, scaling_factor):
    """Extract ROI coordinates from canvas drawing, scaled to original image."""
    if canvas_json is None:
        return None

    objects = canvas_json.get("objects", [])
    if not objects:
        return None

    # Get the last drawn rectangle
    for obj in reversed(objects):
        if obj["type"] == "rect":
            x = int(obj["left"] * scaling_factor)
            y = int(obj["top"] * scaling_factor)
            w = int(obj["width"] * obj.get("scaleX", 1) * scaling_factor)
            h = int(obj["height"] * obj.get("scaleY", 1) * scaling_factor)

            # Ensure coordinates are within image bounds
            img_array = np.array(original_image)
            height, width = img_array.shape[:2]

            x = max(0, min(x, width))
            y = max(0, min(y, height))
            w = min(w, width - x)
            h = min(h, height - y)

            if w > 10 and h > 10:
                return (x, y, x + w, y + h)

    return None


# Header
st.markdown('<h1 class="main-header">📸 OCR Text Scanner</h1>', unsafe_allow_html=True)

# Two column layout
col_left, col_right = st.columns([1, 1], gap="large")

# LEFT COLUMN - Image Upload & Canvas
with col_left:
    st.markdown("### 📥 Upload & Draw ROI")

    # Input method selector - KEY FIX: Only show ONE input method at a time
    input_method = st.radio(
        "Choose input method:",
        ["📁 Upload File", "📷 Use Camera"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # Show ONLY the selected input method
    if input_method == "📁 Upload File":
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["jpg", "jpeg", "png", "bmp"],
            label_visibility="collapsed",
            key="file_uploader"
        )

        if uploaded_file is not None:
            current_id = uploaded_file.file_id
            # Only process if it's a new file
            if st.session_state.last_file_id != current_id:
                st.session_state.original_image = Image.open(uploaded_file)
                st.session_state.last_file_id = current_id
                reset_state()

    else:  # Camera mode
        camera_image = st.camera_input(
            "Take a picture",
            label_visibility="collapsed",
            key="camera_input"
        )

        if camera_image is not None:
            current_id = camera_image.file_id
            # Only process if it's a new capture
            if st.session_state.last_file_id != current_id:
                st.session_state.original_image = Image.open(camera_image)
                st.session_state.last_file_id = current_id
                reset_state()

    # Show canvas if image uploaded
    if st.session_state.original_image is not None:
        st.caption("🖱️ Draw rectangle around text")

        img_array = np.array(st.session_state.original_image)
        height, width = img_array.shape[:2]

        # Calculate compact display size (max 600px)
        max_width = 600
        if width > max_width:
            scale = max_width / width
            display_width = max_width
            display_height = int(height * scale)
        else:
            display_width = width
            display_height = height
            scale = 1.0

        scaling_factor = width / display_width

        # Canvas
        canvas_result = st_canvas(
            fill_color="rgba(0, 255, 0, 0.15)",
            stroke_width=2,
            stroke_color="#00FF00",
            background_image=st.session_state.original_image,
            update_streamlit=True,
            height=display_height,
            width=display_width,
            drawing_mode="rect",
            key=f"canvas_{st.session_state.canvas_key}",
        )

        # Store canvas data
        if canvas_result.json_data is not None:
            st.session_state.canvas_data = canvas_result.json_data

        # Compact control buttons
        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            if st.session_state.canvas_data is not None:
                if st.button("✅ Confirm", type="primary", use_container_width=True):
                    roi_coords = get_roi_from_canvas(
                        st.session_state.canvas_data,
                        st.session_state.original_image,
                        scaling_factor
                    )

                    if roi_coords:
                        x1, y1, x2, y2 = roi_coords
                        cropped = img_array[y1:y2, x1:x2]

                        if cropped.size > 0:
                            st.session_state.cropped_image = Image.fromarray(cropped)
                            st.success("✅ Ready for OCR")
                    else:
                        st.error("⚠️ Draw a rectangle first")
            else:
                st.button("✅ Confirm", disabled=True, use_container_width=True)

        with btn_col2:
            if st.button("🔄 Clear Drawing", use_container_width=True):
                reset_state()
                st.rerun()

    else:
        st.info("👆 Select an input method above to start")

# RIGHT COLUMN - OCR & Results
with col_right:
    st.markdown("### 🔍 Extract Text")

    if st.session_state.cropped_image is not None:
        # Run OCR button (prominent position)
        if st.button("🚀 Run OCR", type="primary", use_container_width=True, key="ocr_btn"):
            with st.spinner("🔄 Processing..."):
                st.session_state.extracted_text = extract_text_from_image(st.session_state.cropped_image)

            if st.session_state.extracted_text.strip():
                st.success("✅ Text extracted!")
            else:
                st.warning("⚠️ No text detected")

        # Show results immediately below button (no scrolling needed!)
        if st.session_state.extracted_text:
            st.markdown("---")

            # Text output
            st.text_area(
                "Extracted Text",
                value=st.session_state.extracted_text,
                height=300,
                label_visibility="visible"
            )

            # Compact stats
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            with stat_col1:
                st.metric("Words", len(st.session_state.extracted_text.split()))
            with stat_col2:
                st.metric("Chars", len(st.session_state.extracted_text))
            with stat_col3:
                lines = len([l for l in st.session_state.extracted_text.split('\n') if l.strip()])
                st.metric("Lines", lines)

            # Action buttons
            act_col1, act_col2 = st.columns(2)

            with act_col1:
                filename = f"text_{time.strftime('%Y%m%d-%H%M%S')}.txt"
                st.download_button(
                    label="💾 Download",
                    data=st.session_state.extracted_text,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True
                )

            with act_col2:
                if st.button("🗑️ Clear Results", use_container_width=True, key="clear_results"):
                    st.session_state.extracted_text = ""
                    st.rerun()

            # Technical details (collapsed by default)
            with st.expander("🔬 Preprocessed Image"):
                preprocessed = preprocess_image(st.session_state.cropped_image)
                st.image(preprocessed, caption="Binary threshold applied", use_column_width=True)

        else:
            st.info("👈 Confirm ROI, then click 'Run OCR'")

    else:
        st.info("👈 Draw and confirm ROI on the left")

        # Compact tips
        st.markdown("#### 💡 Tips")
        st.caption("• Use high-res images\n• Ensure good lighting\n• Keep text horizontal")

# Minimal footer
st.markdown("---")
st.caption("Built with Streamlit & PyTesseract")
