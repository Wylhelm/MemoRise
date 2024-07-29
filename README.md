![MemoRise Logo](static/images/logo.png)

# MemoRise - Memory Augmentation App

MemoRise is a Flask-based web application that helps users store, retrieve, analyze, and interact with their memories. It leverages advanced Natural Language Processing (NLP) and Machine Learning technologies to provide a rich, insightful experience with personal memories.

## Features

- Add and manage text-based memories
- Advanced memory retrieval with multi-faceted search
- Interactive chat interface to query memories
- Automatic categorization and sentiment analysis of memories
- Entity and key phrase extraction
- Language detection
- Memory analytics and visualization
- Export memories in CSV or JSON format

## Technologies Used

- Flask: Web framework
- SQLAlchemy: ORM for database management
- Azure AI Text Analytics: For NLP tasks
- Chart.js: For data visualization
- Bootstrap: For responsive design
- Local LLM (LM Studio): For memory interaction

## Getting Started

1. Clone this repository
2. Create a virtual environment and activate it
3. Install the required dependencies: `pip install -r requirements.txt`
4. Set up your Azure AI services and update the `.env` file with your credentials
5. Run the application: `python run.py`

## Documentation

For more detailed information, please refer to:
- `user_guide.md`: Guide for end-users on how to use the application
- `developer_guide.md`: Technical documentation for developers

## Contributing

Contributions to MemoRise are welcome! Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgements

- Azure AI services for providing powerful NLP capabilities
- The Flask and Python communities for their excellent tools and documentation

For support, feature requests, or bug reports, please open an issue in this repository.
