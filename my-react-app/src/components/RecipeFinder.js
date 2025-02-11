import React, { useState } from "react";
import { Search, PlusCircle, X } from "lucide-react";
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

  const deleteIngredientField = (index) => {
    if (ingredients.length > 1) {
      const updatedIngredients = ingredients.filter((_, i) => i !== index);
      setIngredients(updatedIngredients);
    }
  };

  const handleSearch = () => {
    console.log("Searching for recipes with:", ingredients);
  };

  return (
    <div className="recipe-finder">
      <h1>Recipe Finder</h1>

      <div className="w-full max-w-md">
        {ingredients.map((ingredient, index) => (
          <div key={index} className="input-group">
            <input
              type="text"
              placeholder={`Ingredient ${index + 1}`}
              value={ingredient}
              onChange={(e) => handleIngredientChange(index, e.target.value)}
              className="ingredient-input"
            />
            {ingredients.length > 1 && (
              <button
                onClick={() => deleteIngredientField(index)}
                className="delete-btn"
                aria-label="Delete ingredient"
              >
                <X size={18} />
              </button>
            )}
          </div>
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
