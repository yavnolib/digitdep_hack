import logo from './logo_GPN.png';
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
                        <a href="#" className="headerLink"><span> Главная </span></a>
                        <a href="#" className="headerLink"><span> Продукция </span></a>
                        <a href="#" className="headerLink"><span> Технологии </span></a>
                    </nav>
                </div>
            </div>
        </header>
    );
}