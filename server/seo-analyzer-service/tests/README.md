## Testing Steps:

1. **Setup Test Environment**:
   ```bash
   cd server/seo-analyzer-service
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   python setup.py
   ```

2. **Generate Test Data**:
   ```bash
   python tests/generate_test_data.py
   ```

3. **Run Unit Tests**:
   ```bash
   python run_tests.py
   ```

4. **Run Manual Tests**:
   ```bash
   # Start the service in one terminal
   python main.py
   
   # In another terminal, run manual tests
   python tests/manual_test.py
   ```

5. **Test with Postman**:
   - Import the curl commands into Postman
   - Create a collection for SEO Analyzer API
   - Test each endpoint with various inputs

6. **Check Coverage Report**:
   - Open `htmlcov/index.html` in a browser to see test coverage

This testing strategy provides comprehensive coverage of your SEO Analyzer Service, including unit tests, integration tests, and manual testing tools.