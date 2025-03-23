import os
from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.readers.file import PDFReader
from llama_index.core import SimpleDirectoryReader


def get_index(data, index_name):
    index = None
    if not os.path.exists(index_name):
        print("building index", index_name)
        index = VectorStoreIndex.from_documents(data, show_progress=True)
        index.storage_context.persist(persist_dir=index_name)
    else:
        index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=index_name)
        )

    return index


pdf_reader = PDFReader()

# Load and read the PDF file
wheat_pdf = pdf_reader.load_data(file="data/Wheat Policy Analysis For 2023-24 Crop.pdf")
wheat_index = get_index(wheat_pdf, "wheat")
wheat_engine = wheat_index.as_query_engine()

# Load and read the PDF file
rice_pdf = pdf_reader.load_data(file="data/Rice Policy 2022-23.pdf")
rice_index = get_index(rice_pdf, "rice")
rice_engine = rice_index.as_query_engine()

# Load and read the PDF file
cotton_pdf = pdf_reader.load_data(file="data/Cotton Policy Analysis For 2022-23 Crop.pdf")
cotton_index = get_index(cotton_pdf, "cotton")
cotton_engine = cotton_index.as_query_engine()

reader = SimpleDirectoryReader('./data/spinach/')
spinach_pdf = reader.load_data()
spinach_index = get_index(spinach_pdf, "spinach")
spinach_engine = spinach_index.as_query_engine()

reader = SimpleDirectoryReader('./data/maize/')
maize_pdf = reader.load_data()
maize_index = get_index(maize_pdf, "maize")
maize_engine = maize_index.as_query_engine()

reader = SimpleDirectoryReader('./data/sugarcane/')
sugarcane_pdf = reader.load_data()
sugarcane_index = get_index(sugarcane_pdf, "sugarcane")
sugarcane_engine = sugarcane_index.as_query_engine()