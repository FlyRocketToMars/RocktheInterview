import json, uuid
from pathlib import Path
from datetime import datetime

json_path = Path("data/interview_questions.json")
data = json.load(open(json_path, encoding="utf-8"))
existing = set(q["question"] for q in data["questions"])

QUESTIONS = [
    {"q": "Overfitting/Underfitting是指的什么？", "cat": "fundamentals", "round": "ml_theory", "diff": "easy", "freq": 5},
    {"q": "Bias/Variance trade-off 是指的什么？", "cat": "fundamentals", "round": "ml_theory", "diff": "easy", "freq": 5},
    {"q": "过拟合一般有哪些预防手段？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "Generative和Discriminative Model的区别是什么？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "Given ground truths and 2 models, how do you be confident that one model is better than another?", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 3},
    {"q": "L1 vs L2 Regularization: 各自是什么，有什么区别？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "Lasso/Ridge Regression的解释，Prior分别是什么？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "为什么L1比L2更稀疏(sparse)？", "cat": "fundamentals", "round": "ml_theory", "diff": "hard", "freq": 4},
    {"q": "为什么Regularization works？它的直觉解释是什么？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "为什么Regularization用L1/L2，而不是L3、L4？", "cat": "fundamentals", "round": "ml_theory", "diff": "hard", "freq": 3},
    {"q": "Precision and Recall的定义及trade-off", "cat": "fundamentals", "round": "ml_theory", "diff": "easy", "freq": 5},
    {"q": "Label不平衡时用什么Metric？为什么？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "分类问题该选用什么Metric, and why？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "Confusion Matrix的解释和应用", "cat": "fundamentals", "round": "ml_theory", "diff": "easy", "freq": 5},
    {"q": "AUC的解释: the probability of ranking a randomly selected positive sample higher than a negative one", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "True Positive Rate, False Positive Rate, 以及ROC曲线的解释", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "Log-loss是什么，什么时候用Log-loss？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "用MSE做Loss的Logistic Regression是convex problem吗？", "cat": "fundamentals", "round": "ml_theory", "diff": "hard", "freq": 3},
    {"q": "解释并写出MSE的公式，什么时候用到MSE？", "cat": "fundamentals", "round": "ml_theory", "diff": "easy", "freq": 4},
    {"q": "Linear Regression最小二乘法和MLE的关系", "cat": "fundamentals", "round": "ml_theory", "diff": "hard", "freq": 3},
    {"q": "什么是Relative Entropy/Cross Entropy，以及K-L Divergence？它们的intuition是什么？", "cat": "fundamentals", "round": "ml_theory", "diff": "hard", "freq": 4},
    {"q": "Logistic Regression的Loss是什么？推导过程？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "SVM的Loss是什么？(Hinge Loss)", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "Multiclass分类为什么用Cross Entropy做Cost Function？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "Decision Tree split node的时候优化目标是什么？(Gini/Entropy)", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "DNN为什么要有bias term？Bias term的intuition是什么？", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "什么是Back Propagation？详细解释", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "梯度消失和梯度爆炸是什么？怎么解决？", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "神经网络初始化能不能把weights都initialize成0？为什么？", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "DNN和Logistic Regression的区别？为什么DNN的拟合能力更强？", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "How to do hyperparameter tuning in DL? Random search vs Grid search", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "Deep Learning有哪些预防Overfitting的办法？", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "什么是Dropout，why it works？训练和测试时的区别？", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "什么是Batch Normalization，why it works？训练和测试时的区别？", "cat": "deep_learning", "round": "ml_theory", "diff": "hard", "freq": 5},
    {"q": "Common activation functions (Sigmoid, Tanh, ReLU, Leaky ReLU) 各自的优缺点", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "为什么需要non-linear activation functions？", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "Different optimizers (SGD, RMSprop, Momentum, Adagrad, Adam) 的区别", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "Batch vs SGD的优缺点，Batch size的影响？", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "Learning rate过大过小对模型的影响？", "cat": "deep_learning", "round": "ml_theory", "diff": "easy", "freq": 4},
    {"q": "Plateau和Saddle Point问题是什么？如何解决？", "cat": "deep_learning", "round": "ml_theory", "diff": "hard", "freq": 3},
    {"q": "Linear Regression的基础假设是什么？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "What will happen when we have correlated variables in Linear Regression? How to solve?", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "If the relationship between y and x is nonlinear, can Linear Regression solve that?", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 3},
    {"q": "K-means clustering算法详解：是否会收敛，收敛到global还是local optimum，如何停止？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "EM算法是什么？GMM是什么？和K-means的关系？", "cat": "fundamentals", "round": "ml_theory", "diff": "hard", "freq": 4},
    {"q": "Decision Tree如何split nodes (regression vs classification)？如何防止overfitting？如何做regularization？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "Bagging vs Boosting的区别是什么？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "GBDT和Random Forest的区别，各自的优缺点？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "为什么Random Forest能减少variance？它减少的是bias还是variance？", "cat": "fundamentals", "round": "ml_theory", "diff": "hard", "freq": 4},
    {"q": "和Discriminative模型比，Generative Model更容易overfitting还是underfitting？朴素贝叶斯的原理和假设？", "cat": "fundamentals", "round": "ml_theory", "diff": "hard", "freq": 3},
    {"q": "LDA/QDA是什么？假设是什么？", "cat": "fundamentals", "round": "ml_theory", "diff": "hard", "freq": 3},
    {"q": "Logistic Regression和SVM的区别？(Loss不同、输出不同)", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "Explain SVM: 如何引入非线性？Kernel methods是什么？常见的kernel有哪些？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "Explain PCA: 原理、步骤、应用", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "Explain KNN: 原理、优缺点", "cat": "fundamentals", "round": "ml_theory", "diff": "easy", "freq": 4},
    {"q": "所有常见ML模型的Pros and Cons对比 (最高频面试题)", "cat": "fundamentals", "round": "ml_theory", "diff": "hard", "freq": 5},
    {"q": "怎么处理Imbalanced Data？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "High-dimensional classification有什么问题？如何处理？(Curse of dimensionality)", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "Missing Data如何处理？", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "How to do feature selection? How to capture feature interaction?", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "手写实现两层Fully Connected网络 (forward + backward)", "cat": "deep_learning", "round": "ml_coding", "diff": "hard", "freq": 4},
    {"q": "手写实现K-Means算法", "cat": "fundamentals", "round": "ml_coding", "diff": "medium", "freq": 4},
    {"q": "手写实现KNN算法", "cat": "fundamentals", "round": "ml_coding", "diff": "medium", "freq": 3},
    {"q": "手写Softmax的backpropagation推导", "cat": "deep_learning", "round": "ml_coding", "diff": "hard", "freq": 3},
    {"q": "Convolution layer的output size怎么算？写出公式", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "训练好的模型在现实中不work，可能的原因有哪些？", "cat": "mlops", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "Loss趋于Inf或者NaN的可能原因？", "cat": "deep_learning", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "生产和开发时Data发生了一些shift，如何detect和补救？", "cat": "mlops", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "Annotation有限的情况下怎么train model? (Semi-supervised, Active Learning, Data Augmentation等)", "cat": "mlops", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "模型要上production但发现online有一个important feature missing，不能重新train，怎么办？", "cat": "mlops", "round": "ml_system_design", "diff": "hard", "freq": 3},
    {"q": "LSTM的公式和结构是什么？LSTM比RNN好在哪？", "cat": "nlp", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "Why use RNN/LSTM? Limitation of RNN是什么？如何解决gradient vanishing in RNN？", "cat": "nlp", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "What is Attention mechanism, why attention? Self-attention vs traditional attention?", "cat": "nlp", "round": "ml_theory", "diff": "medium", "freq": 5},
    {"q": "Language Model的原理，N-Gram Model是什么？", "cat": "nlp", "round": "ml_theory", "diff": "medium", "freq": 3},
    {"q": "Word2Vec：CBOW和Skip-gram是什么？Loss function是什么？Negative sampling是什么？", "cat": "nlp", "round": "ml_theory", "diff": "hard", "freq": 4},
    {"q": "MaxPooling, Conv Layer是什么？为什么做pooling？什么是equivariant/invariant to translation？1x1 filter的作用？", "cat": "cv", "round": "ml_theory", "diff": "medium", "freq": 4},
    {"q": "什么是Skip Connection (Residual Connection)？为什么有效？", "cat": "cv", "round": "ml_theory", "diff": "medium", "freq": 4},
]

added = 0
for item in QUESTIONS:
    if item["q"] not in existing:
        entry = {
            "id": f"curated_{str(uuid.uuid4())[:8]}",
            "company": "Community",
            "role": "MLE",
            "level": "L4/L5",
            "round": item["round"],
            "domain": item["cat"],
            "question": item["q"],
            "answer": "ℹ️ 答案待生成（将由 Gemini AI 自动补充）",
            "follow_ups": [],
            "difficulty": item["diff"],
            "frequency": item["freq"],
            "importance": item["freq"],
            "tags": ["curated", "ml-fundamentals", item["cat"]],
            "common_mistakes": [],
            "year": 2026
        }
        data["questions"].append(entry)
        existing.add(item["q"])
        added += 1

data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
data["metadata"]["total_questions"] = len(data["questions"])

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Added {added} questions. Total: {len(data['questions'])}")
