import "./Autolotation.css"
import LoadForm from "../LoadForm/LoadForm";
export default function Autolotion({setMainContent, setBigCard, mainContentRef, dataLoaded, setDataLoaded}) {
    // console.log(setMainContent)
    // const [AutolotationContent, setAutolotationContent] = useState(LoadForm);
    // function Load() {
    //     setAutolotationContent("Loaded");
    // }
    return(
        <div className="autolotation-content">
            <p className="h3">Автоматичкское лотирование заявок на закупку МТР</p>
            {/* { AutolotationContent } */}
            <LoadForm setMainContent={setMainContent} setBigCard={setBigCard} mainContentRef={mainContentRef} dataLoaded={dataLoaded} setDataLoaded={setDataLoaded} />
        </div>
    );
}