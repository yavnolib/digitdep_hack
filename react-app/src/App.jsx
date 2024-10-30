import './App.css';
import { useState, useRef } from 'react';
import Header from './components/Header/Header';
import Footer from './components/Footer/Footer';
import Sidebar from './components/Sidebar/Sidebar';
import Content from './components/Content/Content';
import SampleInstruction from './components/SampleInstruction/SampleInstruction';

export default function App() {
    // const sample = <div className="sample">Для простмотра статистики по лотам загрузите файл по <a className="sample-link" href="#">следующему образцу</a>.</div>
    const [mainContent, setMainContent] = useState(<SampleInstruction />);
    const [bigCard, setBigCard] = useState();
    const [dataLoaded, setDataLoaded] = useState("li");
    const mainContentRef = useRef(null);
    // setDataLoaded("LI");
    return (
        <div className="App">
            <Header  />
            <main>
                
                <Sidebar setMainContent = {setMainContent} setBigCard = {setBigCard} mainContentRef={mainContentRef} dataLoaded={dataLoaded} setDataLoaded={setDataLoaded} />
                <div className="content">
                    <Content mainContent = {mainContent} bigCard = {bigCard} mainContentRef={mainContentRef}/>
                </div>
            </main>
            <Footer />
        </div>
    );
}

