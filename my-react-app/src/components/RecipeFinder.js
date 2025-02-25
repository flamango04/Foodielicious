import React, { useState } from "react";
import { Search, PlusCircle, X } from "lucide-react";
import axios from "axios";
import "./RecipeFinder.css"; 

const RecipeFinder = () => {
  const [ingredients, setIngredients] = useState([]); // 存储用户选定的食材
  const [query, setQuery] = useState(""); // 存储当前输入框的内容
  const [results, setResults] = useState([]); // 存储搜索结果

  // 处理输入框变化
  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  // 添加搜索结果到选定的食材列表
  const handleIngredientClick = (ingredient) => {
    if (!ingredients.includes(ingredient)) {
      setIngredients([...ingredients, ingredient]);
    }
    setQuery(""); // 清空输入框
    setResults([]); // 清空搜索结果
  };

  // 删除已选食材
  const deleteIngredient = (index) => {
    const updatedIngredients = ingredients.filter((_, i) => i !== index);
    setIngredients(updatedIngredients);
  };

  // 发送 API 请求
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

  // 监听回车键（Enter）触发搜索
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="recipe-finder">
      <h1>Recipe Finder</h1>

      {/* 输入框 + 选中的食材展示 */}
      <div className="w-full max-w-md">
        <div className="input-group">
          <input
            type="text"
            placeholder="Enter an ingredient..."
            value={query}
            onChange={handleQueryChange}
            onKeyDown={handleKeyDown} // 监听回车键
            className="ingredient-input"
          />
          <button onClick={handleSearch} className="button search-btn">
            <Search />
          </button>
        </div>

        {/* 已选食材的标签 */}
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

      {/* 搜索结果展示 */}
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
