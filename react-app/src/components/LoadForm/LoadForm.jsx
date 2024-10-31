import "./LoadForm.css"
import { RotatingLines } from "react-loader-spinner";
import xlsx_img from "./xlsx.png"
import React, { useCallback, useEffect, useState } from "react"
import LotCardSmall from "../LotCardSmall/LotCardSmall";
function timeout(delay) {
    return new Promise( res => setTimeout(res, delay) );
}

export default function LoadForm({setMainContent, setBigCard, mainContentRef, dataLoaded, setDataLoaded}) {
    function Loader() {
        return (
          <RotatingLines
            strokeColor="grey"
            strokeWidth="5"
            animationDuration="0.75"
            width="96"
            visible={true}
          />
        )
    }  
    const [data, setData] = useState(null);
    const handleFileLoad = async (event) => {
        const formData = new FormData();
        const file = event.target.files[0];
        // console.log(event.target.files[0]);
        formData.append(file.name, file);
        setMainContent(<Loader/>); // Начало загрузки
        try {
            const response = await fetch("/api/upload", {
                method: "POST",
                body: formData,
            });
            
            const result = await response.json();
            setData(result); 
            console.log(Object.keys(result))
            let cards = [];
            Object.keys(result).forEach(i => {
                // console.log(result[i]);
                cards.push(<LotCardSmall lotNum={i} uniqueMats={result[i]["unique_mats"]} uniqueBuyers={result[i]["unique_buyers"]} numMembers={result[i]["n_members"]} description={result[i]["description"]} lotSum={result[i]["lot_sum"]} isTop={result[i]["is_top"]} setBigCard={setBigCard} mainContentRef={mainContentRef}/>)
                // console.log("OI") // Выводим значение по ключу
            });
            setMainContent(cards)
            // setMainContent(<div>Ответ от сервера: {JSON.stringify(result)}</div>);
            
            // Сохраняем ответ в состояние
        } catch (error) {
            console.error('Ошибка:', error);
        } finally {
            // console.log(data)
            // console.log(dataLoaded)
            // setDataLoaded("LI")
            // console.log()
            // setMainContent(cards) // Останавливаем загрузку
        }
        // console.log(dataLoaded)

    
        // useEffect(() => {
        //     fetch() .then(data => setDataLoaded(data));
        // }, []);

        
    }
    return(
        <form action="load" method="post" id='upload-form'>
            <label htmlFor="file-upload" className="file-upload-label">
                <div className="load-form">
                    <div className="xlsx-img">
                        <img src={xlsx_img} alt="xlsx" />
                    </div>
                    <div className="file-description">
                        <p className="fileD">Загрузить файл</p>
                        <p className="fileD">.xls .xlsx</p>
                    </div>
                </div>
            </label>
            <input id="file-upload" type="file" accept=".xls,.xlsx" onChange={handleFileLoad}/>   
        </form>
    );
}