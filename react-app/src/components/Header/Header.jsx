import logo from './gpn_logo2.png';
import './Header.css'
export default function Header() {
    return (
        <header>
            <div className="container">
                <div className="col2_5">
                    <img src={logo} alt="GPN" id='logo'/>
                </div>
                <div className="col3_5">
                    <nav>
                        <a href="https://www.gazprom-neft.ru/" className="headerLink"><span> Главная </span></a>
                        <a href="https://www.gazprom-neft.ru/products-and-services/" className="headerLink"><span> Продукция </span></a>
                        <a href="https://www.gazprom-neft.ru/products-and-services/for-business/" className="headerLink"><span> Технологии </span></a>
                    </nav>
                </div>
            </div>
        </header>
    );
}