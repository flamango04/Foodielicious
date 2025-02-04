import React, { useState } from "react";
import { Search, PlusCircle } from "lucide-react";
import "./RecipeFinder.css"; // Import the CSS file

const RecipeFinder = () => {
  const [ingredients, setIngredients] = useState([""]);

  const handleIngredientChange = (index, value) => {
    const updatedIngredients = [...ingredients];
    updatedIngredients[index] = value;
    setIngredients(updatedIngredients);
  };

  const addIngredientField = () => {
    setIngredients([...ingredients, ""]);
  };

  const handleSearch = () => {
    console.log("Searching for recipes with:", ingredients);
  };

  return (
    <div className="recipe-finder">
      <h1>Recipe Finder</h1>

      <div className="w-full max-w-md">
        {ingredients.map((ingredient, index) => (
          <input
            key={index}
            type="text"
            placeholder={`Ingredient ${index + 1}`}
            value={ingredient}
            onChange={(e) => handleIngredientChange(index, e.target.value)}
            className="ingredient-input"
          />
        ))}
      </div>

      <div className="button-group">
        <button onClick={addIngredientField} className="button add-btn">
          <PlusCircle /> Add Ingredient
        </button>

        <button onClick={handleSearch} className="button search-btn">
          <Search /> Search Recipes
        </button>
      </div>
    </div>
  );
};

export default RecipeFinder;
