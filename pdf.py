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


#pdf_path = os.path.join("data", "Canada.pdf")
#crops_pdf = SimpleDirectoryReader("./data").load_data()
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

# Load and read the PDF file
sugercane_pdf = pdf_reader.load_data(file="data/SugarcanePolicyAnalysis for 2022-23Crop.pdf")
sugercane_index = get_index(sugercane_pdf, "sugercane")
sugercane_engine = sugercane_index.as_query_engine()

reader = SimpleDirectoryReader('./data/blackberry/')
blackberry_pdf = reader.load_data()
#blackberry_pdf = pdf_reader.load_data(file="data/BlackBerries.pdf")
blackberry_index = get_index(blackberry_pdf, "blackberry")
blackberry_engine = blackberry_index.as_query_engine()

# # Load and read the PDF file
# mnfsr_pdf = pdf_reader.load_data(file="data/mnfsrpublication.pdf")
# mnfsr_index = get_index(mnfsr_pdf, "agriculture statistics")
# mnfsr_engine = mnfsr_index.as_query_engine()