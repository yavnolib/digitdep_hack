import "./Instructions.css"
export default function Instructions() {
    return(
        <div className="insrtrucitons-content">
            <p className="instru">1. Перейдите во вкладку <b> Автолотирование</b> и загрузите в форму файл.</p>
            <p className="instru">2. После обработки файла будут выведены блоки, соответствующие лотам.</p>
            <p className="instru">3. Каждый из блоков можно раскрыть, нажав на него.</p>
            <p className="instru">4. В самом низу страницы находится лот с <b>проблемными заявками</b>.</p>
            <p className="instru"n>5. Нажав на кнопку <b> "Скачать CSV"</b>, можно скачать результат лотирования в виде таблицы.</p>
        </div>
    );
}