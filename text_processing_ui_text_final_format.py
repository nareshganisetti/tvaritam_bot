import streamlit as st
import pandas as pd
from io import BytesIO

def process_input(user_input, prefix="", suffix="", wrapper="", open_wrapper="", close_wrapper="", separator=", ", transform=None, add_numbering=False):
    # Normalize the wrapper input to handle cases like '(' or '()' as the same
    if wrapper in ["(", "()"]:
        open_wrapper, close_wrapper = "(", ")"
    elif wrapper in ["[", "[]"]:
        open_wrapper, close_wrapper = "[", "]"
    elif wrapper in ["{", "{}"]:
        open_wrapper, close_wrapper = "{", "}"
    elif wrapper in ["'", "''"]:
        open_wrapper = close_wrapper = "'"
    elif wrapper in ['"', '""']:
        open_wrapper = close_wrapper = '"'

    # Automatically set closing wrapper if only opening wrapper is provided
    if wrapper and not open_wrapper and not close_wrapper:
        open_wrapper = wrapper
        close_wrapper = {
            '(': ')',
            '[': ']',
            '{': '}',
            '"': '"',
            "'": "'"
        }.get(wrapper, wrapper)  # Match common wrappers or default to the same
    elif open_wrapper and not close_wrapper:
        close_wrapper = {
            '(': ')',
            '[': ']',
            '{': '}',
            '"': '"',
            "'": "'"
        }.get(open_wrapper, open_wrapper)

    # Split the input into lines
    names = user_input.strip().split('\n')
    processed_names = []

    for idx, name in enumerate(names):
        if not name.strip():
            continue  # Skip empty lines

        formatted_name = name.strip()

        # Apply case transformation if specified
        if transform == "uppercase":
            formatted_name = formatted_name.upper()
        elif transform == "lowercase":
            formatted_name = formatted_name.lower()
        elif transform == "capitalize":
            formatted_name = formatted_name.capitalize()

        # Add numbering if enabled
        if add_numbering:
            formatted_name = f"{idx + 1}. {formatted_name}"

        # Wrap only the word (not prefix or suffix) with specified wrappers
        if open_wrapper or close_wrapper:
            formatted_name = f"{open_wrapper}{formatted_name}{close_wrapper}"

        # Add prefix and suffix
        formatted_name = f"{prefix}{formatted_name}{suffix}"

        # Add to processed list
        processed_names.append(formatted_name)

    # Join the processed names with the chosen separator
    return separator.join(processed_names)

# Streamlit App
def main():
    st.title("Advanced Text Processing App")
    st.write("Customize and format your text with ease!")

    # Input Method
    input_method = st.radio("How would you like to provide input?", ["Manually", "Upload a File"])

    if input_method == "Manually":
        user_input = st.text_area("Enter your text (one name per line):")
    else:
        uploaded_file = st.file_uploader("Upload a file containing names:", type=["txt"])
        if uploaded_file is not None:
            user_input = uploaded_file.read().decode("utf-8")
        else:
            user_input = ""

    # Formatting Options
    st.subheader("Formatting Options")
    prefix = st.text_input("Enter a prefix (optional):")
    suffix = st.text_input("Enter a suffix (optional):")
    wrapper = st.text_input("Enter a wrapper (e.g., '(', '[', '{', etc., optional):")

    separator = st.text_input("Enter a separator (default: ','):", value=", ")
    transform = st.selectbox("Transform names:", ["None", "Uppercase", "Lowercase", "Capitalize"])
    add_numbering = st.checkbox("Add numbering to each name")

    # Process Input
    if st.button("Process Text"):
        if user_input:
            result = process_input(
                user_input,
                prefix=prefix,
                suffix=suffix,
                wrapper=wrapper,
                separator=separator,
                transform=transform.lower() if transform != "None" else None,
                add_numbering=add_numbering
            )
            st.subheader("Processed Output")
            st.text_area("", result, height=200)

            # Save Processed Output
            st.subheader("Save Output")
            file_format = st.selectbox("Choose file format to save:", [".txt", ".csv", ".xlsx"])

            processed_list = result.split(separator)  # Split processed output for saving

            if file_format == ".txt":
                st.download_button(
                    label="Download as TXT",
                    data=result,
                    file_name="processed_output.txt",
                    mime="text/plain"
                )

            elif file_format == ".csv":
                csv_data = pd.DataFrame({"Processed Names": processed_list})
                csv_bytes = csv_data.to_csv(index=False).encode('utf-8')  # Convert to bytes
                st.download_button(
                    label="Download as CSV",
                    data=csv_bytes,
                    file_name="processed_output.csv",
                    mime="text/csv"
                )

            elif file_format == ".xlsx":
                xlsx_data = pd.DataFrame({"Processed Names": processed_list})
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    xlsx_data.to_excel(writer, index=False, sheet_name="Processed Output")
                    writer.save()
                buffer.seek(0)  # Move to the start of the stream
                st.download_button(
                    label="Download as XLSX",
                    data=buffer.getvalue(),
                    file_name="processed_output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        else:
            st.error("Please provide some input text.")

if __name__ == "__main__":
    main()
