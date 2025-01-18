# WriteWorld

An AI Writing Assistant built with agentuniverse.

## Quick Start

The easiest way to get started is using the `quick_start.sh` script:

```bash
./quick_start.sh
```

The script will automatically:
1. Install and configure Miniconda if not present
   - Uses Tsinghua mirrors for faster downloads in China
   - Supports both x86_64 and ARM architectures on macOS and Linux
2. Create a Python 3.10 environment named 'writeworld'
3. Install agentuniverse and other dependencies
4. Set up configuration files
   - Creates `custom_key.toml` from sample if not present
   - Configures the custom key path in `config.toml`
5. Start the server application

## Project Structure

```
writeworld/
├── bootstrap/                 # Application entry points
│   ├── server_application.py # Web server entry point
│   └── product_application.py # Product application entry point
├── config/                    # Configuration files
│   ├── config.toml          # Main configuration
│   ├── gunicorn_config.toml # Gunicorn server config
│   └── log_config.toml      # Logging configuration
├── writeworld/               # Main package directory
│   ├── core/                # Core functionality
│   └── test/                # Test files
└── pyproject.toml           # Project dependencies and metadata
```

## Manual Setup and Installation

If you prefer not to use the quick start script, you can set up manually:

1. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

2. Run the server:
   ```bash
   cd bootstrap
   python3 server_application.py
   ```

   Note: The server must be started from within the `bootstrap` directory due to agentuniverse's requirements.

## Important Notes

### Project Structure Requirements

- The project follows the agentuniverse framework structure:
  - Entry point files must be in a `bootstrap` directory at the project root
  - Configuration files should be in a `config` directory at the project root

### Configuration

- Main configuration is in `config/config.toml`
- Custom API keys should be configured in `config/custom_key.toml`
- The server runs on port 8888 by default
- Use `--port` argument to specify a different port if needed

### Known Issues

1. LangChain Deprecation Warning:
   - Current version uses deprecated imports from `langchain`
   - This will be resolved when agentuniverse updates to use `langchain-community`
   - Warning does not affect functionality

## Development

### Testing

Run tests using pytest:
```bash
pytest writeworld/test
```

## License

[Add license information]

## Contributing

[Add contribution guidelines]
