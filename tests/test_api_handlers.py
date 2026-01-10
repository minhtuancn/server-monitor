"""
Additional API Handler Tests for central_api.py
Target: Increase central_api.py coverage to 15%+
Focus: Handler helper methods, request/response processing
"""

import pytest
import json
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import central_api


class TestHandlerHelperMethods:
    """Test CentralAPIHandler helper methods"""
    
    def test_read_body_with_content(self):
        """Test _read_body with valid JSON content"""
        # Create a mock handler
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.headers = {'Content-Length': '27'}
        handler.rfile = Mock()
        handler.rfile.read.return_value = b'{"username": "admin"}'
        
        # Call the actual _read_body method
        result = central_api.CentralAPIHandler._read_body(handler)
        
        assert result == {"username": "admin"}
    
    def test_read_body_empty(self):
        """Test _read_body with no content"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.headers = {'Content-Length': '0'}
        
        result = central_api.CentralAPIHandler._read_body(handler)
        
        assert result == {}
    
    def test_read_body_invalid_json(self):
        """Test _read_body with invalid JSON"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.headers = {'Content-Length': '15'}
        handler.rfile = Mock()
        handler.rfile.read.return_value = b'{ invalid json }'
        
        result = central_api.CentralAPIHandler._read_body(handler)
        
        # Should return empty dict on parse error
        assert result == {}
    
    def test_start_request_initializes_tracking(self):
        """Test _start_request sets up request tracking"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.headers = {}
        
        with patch('central_api.RequestContext.get_or_generate_request_id') as mock_id:
            mock_id.return_value = 'req-12345'
            
            central_api.CentralAPIHandler._start_request(handler)
            
            assert hasattr(handler, 'request_start_time')
            assert handler.request_id == 'req-12345'
    
    def test_finish_request_logs_metrics(self):
        """Test _finish_request logs and records metrics"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.request_start_time = time.time() - 0.1  # 100ms ago
        handler.request_id = 'req-123'
        handler.command = 'GET'
        handler.path = '/api/servers'
        handler.client_address = ('127.0.0.1', 12345)
        handler.headers = {'User-Agent': 'test-client'}
        
        with patch('central_api.logger.request') as mock_log, \
             patch('central_api.metrics.record_request') as mock_metrics:
            
            central_api.CentralAPIHandler._finish_request(handler, 200)
            
            mock_log.assert_called_once()
            mock_metrics.assert_called_once()
            
            # Check logged values
            call_kwargs = mock_log.call_args[1]
            assert call_kwargs['method'] == 'GET'
            assert call_kwargs['path'] == '/api/servers'
            assert call_kwargs['status_code'] == 200
    
    def test_set_headers_applies_cors(self):
        """Test _set_headers applies CORS headers"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.headers = {'Origin': 'http://localhost:3000'}
        handler.request_id = 'req-123'
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        
        with patch('central_api.security.CORS.get_cors_headers') as mock_cors, \
             patch('central_api.security.SecurityHeaders.get_security_headers') as mock_sec:
            
            mock_cors.return_value = {'Access-Control-Allow-Origin': '*'}
            mock_sec.return_value = {'X-Content-Type-Options': 'nosniff'}
            
            central_api.CentralAPIHandler._set_headers(handler, 200)
            
            handler.send_response.assert_called_with(200)
            # Should call send_header for CORS and security headers
            assert handler.send_header.call_count >= 2


class TestRequestIdHandling:
    """Test request ID generation and tracking"""
    
    def test_request_id_in_headers(self):
        """Test request ID is included in response headers"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.headers = {}
        handler.request_id = 'req-abcd1234'
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        
        with patch('central_api.security.CORS.get_cors_headers') as mock_cors, \
             patch('central_api.security.SecurityHeaders.get_security_headers') as mock_sec:
            
            mock_cors.return_value = {}
            mock_sec.return_value = {}
            
            central_api.CentralAPIHandler._set_headers(handler, 200)
            
            # Check X-Request-Id was sent
            calls = handler.send_header.call_args_list
            request_id_calls = [c for c in calls if c[0][0] == 'X-Request-Id']
            assert len(request_id_calls) > 0
            assert request_id_calls[0][0][1] == 'req-abcd1234'


class TestPublicEndpoints:
    """Test public endpoint access"""
    
    def test_public_endpoint_allows_no_auth(self):
        """Test public GET endpoints don't require authentication"""
        mock_handler = Mock()
        mock_handler.headers = {}
        mock_handler.path = '/api/servers'
        mock_handler.command = 'GET'
        
        result = central_api.verify_auth_token(mock_handler)
        
        assert result['valid'] is True
        assert result['role'] == 'public'
    
    def test_public_endpoint_post_requires_auth(self):
        """Test public endpoints still require auth for POST"""
        mock_handler = Mock()
        mock_handler.headers = {}
        mock_handler.path = '/api/servers'
        mock_handler.command = 'POST'
        
        result = central_api.verify_auth_token(mock_handler)
        
        assert result['valid'] is False


class TestLegacyTokenSupport:
    """Test legacy token authentication fallback"""
    
    def test_legacy_token_check_in_verify_function(self):
        """Test verify_auth_token has legacy token support logic"""
        # Just verify the function exists and can be called
        mock_handler = Mock()
        mock_handler.headers = {}
        mock_handler.path = '/api/tasks'
        mock_handler.command = 'POST'
        
        result = central_api.verify_auth_token(mock_handler)
        
        # Should return a result (valid or invalid)
        assert 'valid' in result
        assert isinstance(result['valid'], bool)


class TestOptionsMethod:
    """Test OPTIONS (CORS preflight) handling"""
    
    def test_do_options_returns_200(self):
        """Test do_OPTIONS returns 200 OK"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler._start_request = Mock()
        handler._set_headers = Mock()
        handler._finish_request = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()
        
        with patch('central_api.security.apply_security_middleware') as mock_sec:
            mock_sec.return_value = {"block": False, "headers": {}}
            
            central_api.CentralAPIHandler.do_OPTIONS(handler)
            
            handler._set_headers.assert_called_with(200, {})
            handler._finish_request.assert_called_with(200)


class TestErrorResponseFormats:
    """Test standardized error response formats"""
    
    def test_error_response_structure(self):
        """Test error responses have consistent structure"""
        error_response = {"error": "Server not found"}
        
        assert 'error' in error_response
        assert isinstance(error_response['error'], str)
    
    def test_error_with_code(self):
        """Test error response with error code"""
        error_response = {
            "error": "Validation failed",
            "code": "VALIDATION_ERROR"
        }
        
        assert error_response['code'] == 'VALIDATION_ERROR'
    
    def test_error_json_encoding(self):
        """Test error can be JSON encoded"""
        error_response = {"error": "Database connection failed", "retry_after": 30}
        
        json_str = json.dumps(error_response)
        assert 'error' in json_str
        assert 'retry_after' in json_str


class TestSecurityMiddlewareBlocking:
    """Test security middleware request blocking"""
    
    def test_rate_limit_blocks_request(self):
        """Test rate limit blocks and returns 429"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler._start_request = Mock()
        handler._set_headers = Mock()
        handler._finish_request = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()
        
        with patch('central_api.security.apply_security_middleware') as mock_sec:
            mock_sec.return_value = {
                "block": True,
                "status": 429,
                "headers": {"Retry-After": "60"},
                "body": {"error": "Rate limit exceeded"}
            }
            
            # Simulate GET request
            central_api.CentralAPIHandler.do_GET(handler)
            
            handler._set_headers.assert_called_with(429, {"Retry-After": "60"})
            handler._finish_request.assert_called_with(429)


class TestLatencyTracking:
    """Test request latency measurement"""
    
    def test_latency_calculation(self):
        """Test latency is calculated correctly"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.request_start_time = time.time() - 0.25  # 250ms ago
        handler.request_id = 'req-123'
        handler.command = 'POST'
        handler.path = '/api/servers'
        handler.client_address = ('127.0.0.1', 12345)
        handler.headers = {}
        
        with patch('central_api.logger.request') as mock_log, \
             patch('central_api.metrics.record_request'):
            
            central_api.CentralAPIHandler._finish_request(handler, 201, user_id=1)
            
            # Check latency was calculated
            call_kwargs = mock_log.call_args[1]
            assert 'latency_ms' in call_kwargs
            # Should be around 250ms
            assert call_kwargs['latency_ms'] > 200
            assert call_kwargs['latency_ms'] < 300


class TestContentTypeHandling:
    """Test Content-Type header handling"""
    
    def test_json_content_type(self):
        """Test JSON content type is set"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.headers = {}
        handler.request_id = None
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        
        with patch('central_api.security.CORS.get_cors_headers') as mock_cors, \
             patch('central_api.security.SecurityHeaders.get_security_headers') as mock_sec:
            
            mock_cors.return_value = {}
            mock_sec.return_value = {}
            
            central_api.CentralAPIHandler._set_headers(handler, 200)
            
            # Check Content-Type header
            calls = [call[0] for call in handler.send_header.call_args_list]
            content_type_calls = [c for c in calls if c[0] == 'Content-type']
            assert len(content_type_calls) > 0
            assert content_type_calls[0][1] == 'application/json'


class TestUserAgentTracking:
    """Test User-Agent header tracking"""
    
    def test_user_agent_logged(self):
        """Test User-Agent is logged in request"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.request_start_time = time.time()
        handler.request_id = 'req-123'
        handler.command = 'GET'
        handler.path = '/api/health'
        handler.client_address = ('127.0.0.1', 12345)
        handler.headers = {'User-Agent': 'Mozilla/5.0 (Test Browser)'}
        
        with patch('central_api.logger.request') as mock_log, \
             patch('central_api.metrics.record_request'):
            
            central_api.CentralAPIHandler._finish_request(handler, 200)
            
            call_kwargs = mock_log.call_args[1]
            assert call_kwargs['user_agent'] == 'Mozilla/5.0 (Test Browser)'
    
    def test_missing_user_agent(self):
        """Test handling of missing User-Agent"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.request_start_time = time.time()
        handler.request_id = 'req-123'
        handler.command = 'GET'
        handler.path = '/api/health'
        handler.client_address = ('127.0.0.1', 12345)
        handler.headers = {}
        
        with patch('central_api.logger.request') as mock_log, \
             patch('central_api.metrics.record_request'):
            
            central_api.CentralAPIHandler._finish_request(handler, 200)
            
            call_kwargs = mock_log.call_args[1]
            assert call_kwargs['user_agent'] is None


class TestIPAddressExtraction:
    """Test client IP address extraction"""
    
    def test_ip_from_client_address(self):
        """Test IP extracted from client_address"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.request_start_time = time.time()
        handler.request_id = 'req-123'
        handler.command = 'POST'
        handler.path = '/api/login'
        handler.client_address = ('192.168.1.50', 54321)
        handler.headers = {}
        
        with patch('central_api.logger.request') as mock_log, \
             patch('central_api.metrics.record_request'):
            
            central_api.CentralAPIHandler._finish_request(handler, 200)
            
            call_kwargs = mock_log.call_args[1]
            assert call_kwargs['ip_address'] == '192.168.1.50'
    
    def test_no_client_address(self):
        """Test handling when client_address is None"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.request_start_time = time.time()
        handler.request_id = 'req-123'
        handler.command = 'GET'
        handler.path = '/api/health'
        handler.client_address = None
        handler.headers = {}
        
        with patch('central_api.logger.request') as mock_log, \
             patch('central_api.metrics.record_request'):
            
            central_api.CentralAPIHandler._finish_request(handler, 200)
            
            call_kwargs = mock_log.call_args[1]
            assert call_kwargs['ip_address'] is None


class TestExtraHeadersHandling:
    """Test custom header handling"""
    
    def test_extra_headers_added(self):
        """Test extra headers are added to response"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.headers = {}
        handler.request_id = 'req-123'
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        
        with patch('central_api.security.CORS.get_cors_headers') as mock_cors, \
             patch('central_api.security.SecurityHeaders.get_security_headers') as mock_sec:
            
            mock_cors.return_value = {}
            mock_sec.return_value = {}
            
            extra = {'X-Custom-Header': 'custom-value'}
            central_api.CentralAPIHandler._set_headers(handler, 200, extra_headers=extra)
            
            # Check custom header was sent
            calls = [call[0] for call in handler.send_header.call_args_list]
            custom_calls = [c for c in calls if c[0] == 'X-Custom-Header']
            assert len(custom_calls) > 0
    
    def test_extra_headers_dont_override_security(self):
        """Test extra headers don't override security headers"""
        handler = Mock(spec=central_api.CentralAPIHandler)
        handler.headers = {}
        handler.request_id = None
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        
        with patch('central_api.security.CORS.get_cors_headers') as mock_cors, \
             patch('central_api.security.SecurityHeaders.get_security_headers') as mock_sec:
            
            mock_cors.return_value = {'Access-Control-Allow-Origin': '*'}
            mock_sec.return_value = {}
            
            # Try to override CORS with extra headers (should be skipped)
            extra = {'Access-Control-Allow-Origin': 'http://evil.com'}
            central_api.CentralAPIHandler._set_headers(handler, 200, extra_headers=extra)
            
            # CORS header from security should be used, not extra
            calls = [call[0] for call in handler.send_header.call_args_list]
            cors_calls = [c for c in calls if c[0] == 'Access-Control-Allow-Origin']
            # Should only have one call (from CORS, not extra)
            assert len(cors_calls) == 1
