import React, { useState } from "react";
import { Search, PlusCircle, X } from "lucide-react";
import axios from "axios";
import "./RecipeFinder.css"; 

const RecipeFinder = () => {
  const [ingredients, setIngredients] = useState([]); 
  const [query, setQuery] = useState(""); 
  const [results, setResults] = useState([]);

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleIngredientClick = (ingredient) => {
    if (!ingredients.includes(ingredient)) {
      setIngredients([...ingredients, ingredient]);
    }
    setQuery(""); 
    setResults([]); 
  };

  const deleteIngredient = (index) => {
    const updatedIngredients = ingredients.filter((_, i) => i !== index);
    setIngredients(updatedIngredients);
  };

  const handleSearch = async () => {
    if (!query) return;
    try {
      const response = await axios.post("http://localhost:8000/search/", {
        keyword: query,
      });
      setResults(response.data.results);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="recipe-finder">
      <h1>Recipe Finder</h1>

      {}
      <div className="w-full max-w-md">
        <div className="input-group">
          <input
            type="text"
            placeholder="Enter an ingredient..."
            value={query}
            onChange={handleQueryChange}
            onKeyDown={handleKeyDown} 
            className="ingredient-input"
          />
          <button onClick={handleSearch} className="button search-btn">
            <Search />
          </button>
        </div>

        {}
        <div className="selected-ingredients">
          {ingredients.map((ingredient, index) => (
            <div key={index} className="ingredient-chip">
              {ingredient}
              <button onClick={() => deleteIngredient(index)} className="delete-chip">
                <X size={12} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {}
      {results.length > 0 && (
        <div className="results">
          <h2>Matching Ingredients</h2>
          <ul>
            {results.map((item, index) => (
              <li key={index} className="result-item" onClick={() => handleIngredientClick(item.raw_ingr)}>
                {item.raw_ingr} (Similarity: {item.similarity.toFixed(2)})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default RecipeFinder;
