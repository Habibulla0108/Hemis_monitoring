import React from 'react';

const TopBar: React.FC = () => {
    return (
        <header style={{
            height: '60px',
            borderBottom: '1px solid #ddd',
            display: 'flex',
            alignItems: 'center',
            padding: '0 20px',
            backgroundColor: '#fff'
        }}>
            <h2 style={{ margin: 0 }}>HEMIS Monitoring</h2>
        </header>
    );
};

export default TopBar;
