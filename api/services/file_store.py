"""Contains functions to perform file operations"""
import tempfile
import io
from django.core.files.uploadedfile import InMemoryUploadedFile

def create_temp_file_with_text(text):
    # Create a temporary file in the temp directory
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+t', suffix='.txt')

    # Write the provided text to the file
    temp_file.write(text)

    # Close the file so it can be read later
    temp_file.close()

    return temp_file.name

def create_inmemory_uploaded_file(description, request):
    # Convert the description string into a file-like object in memory
    # Use io.BytesIO for binary content (which is suitable for file fields)
    # For text content, you can use io.StringIO, but we need binary data here
    byte_io = io.BytesIO(description.encode('utf-8'))  # Convert string to bytes

    # Create an InMemoryUploadedFile from the BytesIO object
    # The 'file' argument here is the file-like object (byte_io)
    # The second argument ('txt') is the file name, and 'txt' is the file type.
    uploaded_file = InMemoryUploadedFile(
        byte_io,              # The file object
        field_name='file',    # The name of the form field for the file
        name='description.txt',  # The filename you want to give the file
        content_type='text/plain',  # The MIME type (text file)
        size=len(description.encode('utf-8')),  # File size in bytes
        charset=None          # No need for charset as we're handling text
    )

    # Attach the uploaded file to the request's FILES attribute
    request.FILES['file'] = uploaded_file

    mutable_data = request.data.copy()  # Make request.data mutable
    mutable_data['file'] = uploaded_file  # Add the file to the copied data
    print("mutable_data", mutable_data)
    return mutable_data