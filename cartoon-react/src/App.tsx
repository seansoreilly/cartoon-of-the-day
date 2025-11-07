import Layout from './components/layout/Layout';
import ErrorBoundary from './components/common/ErrorBoundary';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <Layout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Welcome to Cartoon of the Day
          </h2>
          <p className="text-gray-600 mb-6">
            Generating AI-powered political cartoons based on local news
          </p>
          <button className="btn-primary">
            Get Started
          </button>
        </div>
      </Layout>
    </ErrorBoundary>
  );
}

export default App;
