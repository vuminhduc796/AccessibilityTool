import logo from './logo.svg';
import './App.css';
import { ThemeProvider } from "styled-components";
import GlobalStyle from "./styles/GlobalStyles";
import { Home } from './components/home';
import { AppContext } from './context/Context';
const theme = {
  darkBlueColor: "#223843",
  greenColor: "#768948",
  lightGreyColor: "#E0E0E2",
  darkGreyColor: "#aeaeae",
  lightBlueColor: "#7389AE",
  normalBlueColor: "#416788",
  backgroundBlueColor : "#aecbe4",
  hiddenTextColor: "#A1A4B2",
  backgroundColor: "#F9F0E3",
  darkTextColor : "#1b1b1e",
  inputFieldColor: "#E8E8E8",

  titleSize: "40px",
  sectionHeadingSize: "32px",
  normalTextSize: "18px",

  headingFont: "Denk One",
  normalFont: "Inter",

  elementNormalHeight: "40px",
};

function App() {
  return (
    
    <ThemeProvider theme={theme}>
    <GlobalStyle />
      <div className="App">
          <Home/>
      </div>
  </ThemeProvider>

  );
}

export default App;
