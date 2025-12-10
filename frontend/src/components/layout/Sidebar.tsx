import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
    return (
        <aside style={{
            width: '240px',
            borderRight: '1px solid #ddd',
            height: 'calc(100vh - 60px)',
            backgroundColor: '#f9f9f9',
            padding: '20px'
        }}>
            <nav>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                    <li>
                        <NavLink
                            to="/"
                            style={({ isActive }) => ({
                                display: 'block',
                                padding: '10px',
                                color: isActive ? 'blue' : 'black',
                                fontWeight: isActive ? 'bold' : 'normal',
                                textDecoration: 'none'
                            })}
                        >
                            Dashboard
                        </NavLink>
                    </li>
                </ul>
            </nav>
        </aside>
    );
};

export default Sidebar;
