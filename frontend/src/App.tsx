// Main App Component for FortiGate Network Monitor Pro
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './index.css';

// Import components
import Dashboard from './components/Dashboard';
import DeviceList from './components/DeviceList';
import NetworkTopology from './components/NetworkTopology';
import VulnerabilityDashboard from './components/VulnerabilityDashboard';

// Import services
import { apiService } from './services/api';
import { webSocketService } from './services/websocket';

// Import context
import { DeviceProvider } from './contexts/DeviceContext';

// Import types
import { Device, ScanResult } from './types/device.types';

interface AppState {
  currentView: 'dashboard' | 'devices' | 'topology' | 'vulnerabilities';
  isConnected: boolean;
  loading: boolean;
  error: string | null;
}

const App: React.FC = () => {
  const [state, setState] = useState<AppState>({
    currentView: 'dashboard',
    isConnected: false,
    loading: true,
    error: null
  });

  useEffect(() => {
    initializeApp();
    return () => {
      webSocketService.disconnect();
    };
  }, []);

  const initializeApp = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      // Test API connection
      const healthResponse = await apiService.checkHealth();
      
      if (healthResponse.status === 'healthy') {
        setState(prev => ({ ...prev, isConnected: true }));
        
        // Initialize WebSocket connection
        webSocketService.connect();
        
        // Setup WebSocket event handlers
        webSocketService.onDeviceUpdate((device: Device) => {
          console.log('Device updated:', device);
          // Device updates will be handled by DeviceContext
        });
        
        webSocketService.onScanComplete((scanResult: ScanResult) => {
          console.log('Scan completed:', scanResult);
          // Show notification or update UI
        });
        
      } else {
        throw new Error('API health check failed');
      }
      
    } catch (error) {
      console.error('Failed to initialize app:', error);
      setState(prev => ({ 
        ...prev, 
        error: 'Failed to connect to backend services. Please check your configuration.',
        isConnected: false 
      }));
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  const handleViewChange = (view: AppState['currentView']) => {
    setState(prev => ({ ...prev, currentView: view }));
  };

  const renderCurrentView = () => {
    switch (state.currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'devices':
        return <DeviceList />;
      case 'topology':
        return <NetworkTopology />;
      case 'vulnerabilities':
        return <VulnerabilityDashboard />;
      default:
        return <Dashboard />;
    }
  };

  if (state.loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <h2>Initializing FortiGate Network Monitor Pro...</h2>
        <p>Connecting to backend services...</p>
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="app-error">
        <h2>Connection Error</h2>
        <p>{state.error}</p>
        <button onClick={initializeApp} className="retry-button">
          Retry Connection
        </button>
      </div>
    );
  }