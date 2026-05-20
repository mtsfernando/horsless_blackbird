import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

function Layout() {
  return (
    <div className="layout">
      <Navbar />
      <main>
        <div className="container">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default Layout;
