"""
Inventory Agent module for the AI Inventory Optimization System.

This module provides the inventory management agent that optimizes
inventory levels, calculates reorder points, and minimizes costs.
"""

import logging
import json
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from utils.inventory_optimizer import (
    calculate_reorder_point,
    calculate_economic_order_quantity,
    calculate_stockout_risk,
    optimize_inventory_allocation,
    analyze_inventory_turnover
)
from models import Product, Store, InventoryRecord, db

logger = logging.getLogger(__name__)

class InventoryAgent(BaseAgent):
    """
    Inventory management agent that optimizes inventory levels,
    calculates reorder points, and minimizes costs.
    """
    
    def __init__(self):
        """Initialize the inventory agent."""
        super().__init__(agent_type="inventory")
    
    def calculate_reorder_point(self, product_id, store_id, lead_time_days=3, service_level=0.95):
        """
        Calculate the optimal reorder point for a product at a store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            lead_time_days: Supplier lead time in days
            service_level: Desired service level (0-1)
            
        Returns:
            Dictionary with reorder point information
        """
        try:
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Calculate reorder point
            result = calculate_reorder_point(product_id, store_id, lead_time_days, service_level)
            
            if "error" in result:
                return result
            
            # Log the agent action
            self.log_action(
                action="Reorder point calculation",
                product_id=product_id,
                store_id=store_id,
                details={
                    "lead_time_days": lead_time_days,
                    "service_level": service_level,
                    "reorder_point": result.get("reorder_point", 0),
                    "safety_stock": result.get("safety_stock", 0)
                }
            )
            
            # Add product and store names to the response
            result["product_name"] = product.name
            result["store_name"] = store.name
            
            # Generate explanation
            explanation = self._explain_reorder_point(result, product, store)
            result["explanation"] = explanation
            
            return result
        
        except Exception as e:
            logger.error(f"Error calculating reorder point: {str(e)}")
            return {
                "error": f"Failed to calculate reorder point: {str(e)}"
            }
    
    def calculate_economic_order_quantity(self, product_id, store_id, holding_cost_pct=0.25, order_cost=25.0, days=365):
        """
        Calculate the economic order quantity (EOQ) for a product at a store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            holding_cost_pct: Annual holding cost as a percentage of item value
            order_cost: Fixed cost per order
            days: Number of days to consider for annual demand
            
        Returns:
            Dictionary with EOQ information
        """
        try:
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Calculate EOQ
            result = calculate_economic_order_quantity(
                product_id, store_id, holding_cost_pct, order_cost, days
            )
            
            if "error" in result:
                return result
            
            # Log the agent action
            self.log_action(
                action="Economic order quantity calculation",
                product_id=product_id,
                store_id=store_id,
                details={
                    "holding_cost_pct": holding_cost_pct,
                    "order_cost": order_cost,
                    "eoq": result.get("eoq", 0),
                    "total_annual_cost": result.get("total_annual_cost", 0)
                }
            )
            
            # Add product and store names to the response
            result["product_name"] = product.name
            result["store_name"] = store.name
            
            # Generate explanation
            explanation = self._explain_eoq(result, product, store)
            result["explanation"] = explanation
            
            return result
        
        except Exception as e:
            logger.error(f"Error calculating EOQ: {str(e)}")
            return {
                "error": f"Failed to calculate EOQ: {str(e)}"
            }
    
    def calculate_stockout_risk(self, product_id, store_id, days=30):
        """
        Calculate the risk of stockout for a product at a store within a time period.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            days: Number of days to consider
            
        Returns:
            Dictionary with stockout risk information
        """
        try:
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Get current inventory level
            inventory = db.session.query(InventoryRecord).filter_by(
                product_id=product_id, store_id=store_id
            ).first()
            
            if not inventory:
                return {
                    "error": f"No inventory record found for product {product_id} at store {store_id}"
                }
            
            # Calculate stockout risk
            result = calculate_stockout_risk(
                product_id, store_id, inventory.quantity, days
            )
            
            if "error" in result:
                return result
            
            # Log the agent action
            self.log_action(
                action="Stockout risk calculation",
                product_id=product_id,
                store_id=store_id,
                details={
                    "current_stock": inventory.quantity,
                    "days": days,
                    "risk_level": result.get("risk_level", "unknown"),
                    "stockout_probability": result.get("stockout_probability", 0)
                }
            )
            
            # Add product and store names to the response
            result["product_name"] = product.name
            result["store_name"] = store.name
            
            # Generate recommendation
            recommendation = self._generate_stockout_recommendation(result, product, store)
            result["recommendation"] = recommendation
            
            return result
        
        except Exception as e:
            logger.error(f"Error calculating stockout risk: {str(e)}")
            return {
                "error": f"Failed to calculate stockout risk: {str(e)}"
            }
    
    def optimize_inventory_allocation(self, product_id, total_stock):
        """
        Optimize the allocation of limited inventory across all stores.
        
        Args:
            product_id: ID of the product
            total_stock: Total stock available for allocation
            
        Returns:
            Dictionary with allocation results
        """
        try:
            # Get product to check if it exists
            product = self.get_product(product_id)
            
            if not product:
                logger.error(f"Product {product_id} not found")
                return {
                    "error": f"Product {product_id} not found"
                }
            
            # Get all stores
            stores = db.session.query(Store).all()
            
            if not stores:
                return {
                    "error": "No stores found in the system"
                }
            
            # Extract store IDs
            store_ids = [store.id for store in stores]
            
            # Optimize allocation
            result = optimize_inventory_allocation(
                product_id, store_ids, total_stock
            )
            
            if "error" in result:
                return result
            
            # Log the agent action
            self.log_action(
                action="Inventory allocation optimization",
                product_id=product_id,
                details={
                    "total_stock": total_stock,
                    "total_demand": result.get("total_demand", 0),
                    "coverage_pct": result.get("coverage_pct", 0),
                    "allocation_strategy": result.get("allocation_strategy", "unknown")
                }
            )
            
            # Add product name to the response
            result["product_name"] = product.name
            
            # Add store names to each allocation item
            store_map = {store.id: store.name for store in stores}
            
            for item in result.get("allocation", []):
                store_id = item.get("store_id")
                item["store_name"] = store_map.get(store_id, f"Store {store_id}")
            
            # Generate summary
            summary = self._generate_allocation_summary(result, product)
            result["summary"] = summary
            
            return result
        
        except Exception as e:
            logger.error(f"Error optimizing inventory allocation: {str(e)}")
            return {
                "error": f"Failed to optimize inventory allocation: {str(e)}"
            }
    
    def analyze_inventory_turnover(self, product_id, store_id, days=90):
        """
        Analyze inventory turnover ratio and related metrics.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            days: Number of days to analyze
            
        Returns:
            Dictionary with inventory turnover analysis
        """
        try:
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Get current inventory level
            inventory = db.session.query(InventoryRecord).filter_by(
                product_id=product_id, store_id=store_id
            ).first()
            
            if not inventory:
                return {
                    "error": f"No inventory record found for product {product_id} at store {store_id}"
                }
            
            # Analyze turnover
            result = analyze_inventory_turnover(
                product_id, store_id, inventory.quantity, days
            )
            
            if "error" in result:
                return result
            
            # Log the agent action
            self.log_action(
                action="Inventory turnover analysis",
                product_id=product_id,
                store_id=store_id,
                details={
                    "current_stock": inventory.quantity,
                    "days": days,
                    "turnover_ratio": result.get("inventory_turnover_ratio", 0),
                    "turnover_rating": result.get("turnover_rating", "unknown")
                }
            )
            
            # Add product and store names to the response
            result["product_name"] = product.name
            result["store_name"] = store.name
            
            # Generate recommendation
            recommendation = self._generate_turnover_recommendation(result, product, store)
            result["recommendation"] = recommendation
            
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing inventory turnover: {str(e)}")
            return {
                "error": f"Failed to analyze inventory turnover: {str(e)}"
            }
    
    def get_inventory_optimization_overview(self, store_id=None):
        """
        Get an overview of inventory optimization opportunities.
        
        Args:
            store_id: Optional store ID to filter by
            
        Returns:
            Dictionary with optimization opportunities
        """
        try:
            # Get all inventory records, optionally filtered by store
            query = db.session.query(InventoryRecord)
            
            if store_id:
                store = self.get_store(store_id)
                if not store:
                    return {
                        "error": f"Store {store_id} not found"
                    }
                
                query = query.filter_by(store_id=store_id)
            
            # Get all inventory records
            inventory_records = query.all()
            
            if not inventory_records:
                return {
                    "error": "No inventory records found"
                }
            
            # Analyze each inventory record
            low_stock_items = []
            overstocked_items = []
            optimal_items = []
            
            for record in inventory_records[:10]:  # Limit to 10 for performance
                product = self.get_product(record.product_id)
                store = self.get_store(record.store_id)
                
                if not product or not store:
                    continue
                
                # Calculate stockout risk
                risk_data = calculate_stockout_risk(
                    record.product_id, record.store_id, record.quantity, days=30
                )
                
                # Calculate turnover
                turnover_data = analyze_inventory_turnover(
                    record.product_id, record.store_id, record.quantity, days=90
                )
                
                # Categorize based on risk and turnover
                risk_level = risk_data.get("risk_level", "medium")
                turnover_rating = turnover_data.get("turnover_rating", "average")
                
                item = {
                    "product_id": record.product_id,
                    "product_name": product.name,
                    "store_id": record.store_id,
                    "store_name": store.name,
                    "current_stock": record.quantity,
                    "risk_level": risk_level,
                    "stockout_probability": risk_data.get("stockout_probability", 0),
                    "days_until_stockout": risk_data.get("days_until_stockout"),
                    "turnover_ratio": turnover_data.get("inventory_turnover_ratio"),
                    "turnover_rating": turnover_rating,
                    "last_updated": record.last_updated.strftime("%Y-%m-%d %H:%M")
                }
                
                if risk_level == "high":
                    low_stock_items.append(item)
                elif turnover_rating in ["poor"]:
                    overstocked_items.append(item)
                else:
                    optimal_items.append(item)
            
            # Generate summary
            store_name = None
            if store_id:
                store = self.get_store(store_id)
                if store:
                    store_name = store.name
            
            # Generate natural language summary using LLM if available
            if store_name:
                prompt = f"""
                Please provide a brief overview of the inventory status at {store_name}.
                
                Key metrics:
                - {len(low_stock_items)} items at risk of stockout
                - {len(overstocked_items)} overstocked items
                - {len(optimal_items)} items at optimal levels
                
                What are the most urgent inventory issues that should be addressed,
                and what general recommendation would you give to the store manager?
                """
            else:
                prompt = f"""
                Please provide a brief overview of the inventory status across all stores.
                
                Key metrics:
                - {len(low_stock_items)} items at risk of stockout
                - {len(overstocked_items)} overstocked items
                - {len(optimal_items)} items at optimal levels
                
                What are the most urgent inventory issues that should be addressed,
                and what general recommendation would you give to the inventory manager?
                """
            
            system_prompt = """
            You are a helpful AI assistant specializing in inventory management and optimization.
            Provide concise, actionable insights based on the data provided.
            Focus on the most urgent issues and provide practical recommendations.
            """
            
            summary = self.analyze_with_llm(prompt, system_prompt)
            
            if not summary:
                # Fallback if LLM is not available
                if store_name:
                    summary = (
                        f"At {store_name}, {len(low_stock_items)} items are at risk of stockout and require immediate attention. "
                        f"Additionally, {len(overstocked_items)} items appear to be overstocked with poor turnover ratios, "
                        f"suggesting excess capital tied up in inventory. Consider placing orders for the at-risk items "
                        f"and developing promotions to reduce the overstocked inventory levels."
                    )
                else:
                    summary = (
                        f"Across all stores, {len(low_stock_items)} items are at risk of stockout and require immediate attention. "
                        f"Additionally, {len(overstocked_items)} items appear to be overstocked with poor turnover ratios, "
                        f"suggesting excess capital tied up in inventory. Consider optimizing inventory allocation "
                        f"between stores and adjusting order quantities to address these imbalances."
                    )
            
            # Log the agent action
            self.log_action(
                action="Inventory optimization overview",
                store_id=store_id,
                details={
                    "low_stock_count": len(low_stock_items),
                    "overstocked_count": len(overstocked_items),
                    "optimal_count": len(optimal_items)
                }
            )
            
            return {
                "store_id": store_id,
                "store_name": store_name,
                "summary": summary,
                "low_stock_items": low_stock_items,
                "overstocked_items": overstocked_items,
                "optimal_items": optimal_items,
                "total_items_analyzed": len(low_stock_items) + len(overstocked_items) + len(optimal_items),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        except Exception as e:
            logger.error(f"Error getting inventory optimization overview: {str(e)}")
            return {
                "error": f"Failed to get inventory optimization overview: {str(e)}"
            }
    
    def _explain_reorder_point(self, result, product, store):
        """Generate an explanation for reorder point calculation."""
        try:
            reorder_point = result.get("reorder_point", 0)
            lead_time_days = result.get("lead_time_days", 0)
            safety_stock = result.get("safety_stock", 0)
            service_level = result.get("service_level", 0) * 100
            
            # Generate explanation using LLM if available
            prompt = f"""
            Please explain the following reorder point calculation in clear, concise language:
            
            Product: {product.name}
            Store: {store.name}
            Reorder Point: {reorder_point} units
            Lead Time: {lead_time_days} days
            Safety Stock: {round(safety_stock, 1)} units
            Service Level: {service_level}%
            
            Explain what this means in practical terms for inventory management.
            Keep it brief and actionable, 2-3 sentences.
            """
            
            explanation = self.analyze_with_llm(prompt)
            
            if not explanation:
                # Fallback if LLM is not available
                explanation = (
                    f"For {product.name} at {store.name}, you should place a new order when inventory reaches {reorder_point} units. "
                    f"This includes {round(safety_stock, 1)} units of safety stock to maintain a {service_level}% service level during "
                    f"the {lead_time_days}-day supplier lead time. Monitoring inventory levels and placing orders at this reorder point "
                    f"will help prevent stockouts while minimizing excess inventory."
                )
            
            return explanation
        
        except Exception as e:
            logger.error(f"Error generating reorder point explanation: {str(e)}")
            return "Error generating explanation"
    
    def _explain_eoq(self, result, product, store):
        """Generate an explanation for EOQ calculation."""
        try:
            eoq = result.get("eoq", 0)
            annual_demand = result.get("annual_demand", 0)
            orders_per_year = result.get("orders_per_year", 0)
            days_between_orders = result.get("days_between_orders", 0)
            total_annual_cost = result.get("total_annual_cost", 0)
            
            # Generate explanation using LLM if available
            prompt = f"""
            Please explain the following Economic Order Quantity (EOQ) calculation in clear, concise language:
            
            Product: {product.name}
            Store: {store.name}
            EOQ: {eoq} units
            Annual Demand: {annual_demand} units
            Orders Per Year: {orders_per_year}
            Days Between Orders: {days_between_orders} days
            Total Annual Cost: ${total_annual_cost}
            
            Explain what this means in practical terms for inventory management.
            Keep it brief and actionable, 3-4 sentences.
            """
            
            explanation = self.analyze_with_llm(prompt)
            
            if not explanation:
                # Fallback if LLM is not available
                explanation = (
                    f"For {product.name} at {store.name}, the optimal order quantity is {eoq} units, which should be ordered "
                    f"approximately every {round(days_between_orders)} days ({orders_per_year} times per year). This order quantity "
                    f"minimizes the total annual cost of ordering and holding inventory, estimated at ${round(total_annual_cost)}. "
                    f"By following this ordering pattern, you can efficiently manage the annual demand of {annual_demand} units while "
                    f"keeping inventory costs at a minimum."
                )
            
            return explanation
        
        except Exception as e:
            logger.error(f"Error generating EOQ explanation: {str(e)}")
            return "Error generating explanation"
    
    def _generate_stockout_recommendation(self, result, product, store):
        """Generate a recommendation based on stockout risk."""
        try:
            risk_level = result.get("risk_level", "low").lower()
            stockout_probability = result.get("stockout_probability", 0)
            days_until_stockout = result.get("days_until_stockout")
            stockout_date = result.get("stockout_date")
            current_stock = result.get("current_stock", 0)
            forecasted_demand = result.get("forecasted_demand", 0)
            
            # Generate recommendation using LLM if available
            prompt = f"""
            Please provide a brief, actionable recommendation based on the following stockout risk analysis:
            
            Product: {product.name}
            Store: {store.name}
            Current Stock: {current_stock} units
            Forecasted Demand (30 days): {forecasted_demand} units
            Risk Level: {risk_level}
            Stockout Probability: {stockout_probability}%
            {"Days Until Stockout: " + str(days_until_stockout) if days_until_stockout else ""}
            {"Expected Stockout Date: " + stockout_date if stockout_date else ""}
            
            Provide 1-2 specific actions that should be taken based on this risk assessment.
            """
            
            recommendation = self.analyze_with_llm(prompt)
            
            if not recommendation:
                # Fallback if LLM is not available
                if risk_level == "high":
                    recommendation = (
                        f"URGENT: Place an order for {product.name} immediately. Current stock of {current_stock} units "
                        f"is projected to run out in approximately {days_until_stockout} days (around {stockout_date}), "
                        f"with a {stockout_probability}% probability of stockout within 30 days. Consider expediting "
                        f"shipping to prevent customer service issues."
                    )
                elif risk_level == "medium":
                    recommendation = (
                        f"Monitor {product.name} inventory closely and prepare to place an order within the next week. "
                        f"Current stock of {current_stock} units may be insufficient to meet the projected 30-day demand "
                        f"of {forecasted_demand} units, with a {stockout_probability}% chance of stockout. Review lead times "
                        f"with suppliers to ensure timely replenishment."
                    )
                else:
                    recommendation = (
                        f"No immediate action required for {product.name}. Current stock of {current_stock} units is "
                        f"adequate to meet the projected 30-day demand of {forecasted_demand} units, with only a "
                        f"{stockout_probability}% chance of stockout. Continue with regular inventory monitoring and "
                        f"standard ordering procedures."
                    )
            
            return recommendation
        
        except Exception as e:
            logger.error(f"Error generating stockout recommendation: {str(e)}")
            return "Error generating recommendation"
    
    def _generate_turnover_recommendation(self, result, product, store):
        """Generate a recommendation based on inventory turnover analysis."""
        try:
            turnover_ratio = result.get("inventory_turnover_ratio")
            turnover_rating = result.get("turnover_rating", "average").lower()
            days_of_supply = result.get("days_of_supply")
            current_stock = result.get("current_stock", 0)
            avg_daily_demand = result.get("avg_daily_demand", 0)
            
            # Generate recommendation using LLM if available
            prompt = f"""
            Please provide a brief, actionable recommendation based on the following inventory turnover analysis:
            
            Product: {product.name}
            Store: {store.name}
            Current Stock: {current_stock} units
            Average Daily Demand: {avg_daily_demand} units
            Inventory Turnover Ratio: {turnover_ratio if turnover_ratio else 'N/A'}
            Turnover Rating: {turnover_rating}
            Days of Supply: {days_of_supply if days_of_supply else 'N/A'}
            
            Provide 1-2 specific actions that should be taken to optimize inventory levels
            based on this turnover analysis.
            """
            
            recommendation = self.analyze_with_llm(prompt)
            
            if not recommendation:
                # Fallback if LLM is not available
                if turnover_rating == "poor":
                    recommendation = (
                        f"Reduce inventory levels for {product.name}. The current turnover ratio of {turnover_ratio} is poor, "
                        f"indicating excess inventory relative to demand. With {days_of_supply} days of supply on hand, "
                        f"consider reducing order quantities or developing promotions to accelerate sales. This will free up "
                        f"capital and warehouse space for better-performing products."
                    )
                elif turnover_rating == "excellent":
                    recommendation = (
                        f"Current inventory management for {product.name} is excellent with a turnover ratio of {turnover_ratio}. "
                        f"Maintain current ordering patterns, but monitor closely as high turnover can sometimes indicate risk "
                        f"of stockouts. The current {days_of_supply} days of supply suggests efficient inventory levels. "
                        f"Consider using this product as a benchmark for other inventory optimization efforts."
                    )
                else:
                    recommendation = (
                        f"Current inventory management for {product.name} is adequate with a turnover ratio of {turnover_ratio}. "
                        f"There is room for improvement by fine-tuning order quantities. With {days_of_supply} days of supply, "
                        f"consider slight reductions in order quantities while monitoring stockout risk. Review supplier lead times "
                        f"and consider adjusting reorder points to optimize further."
                    )
            
            return recommendation
        
        except Exception as e:
            logger.error(f"Error generating turnover recommendation: {str(e)}")
            return "Error generating recommendation"
    
    def _generate_allocation_summary(self, result, product):
        """Generate a summary for inventory allocation."""
        try:
            total_stock = result.get("total_stock", 0)
            total_demand = result.get("total_demand", 0)
            coverage_pct = result.get("coverage_pct", 0)
            allocation_strategy = result.get("allocation_strategy", "")
            allocation = result.get("allocation", [])
            
            # Count stores with different coverage levels
            low_coverage = sum(1 for a in allocation if a.get("coverage", 0) < 80)
            good_coverage = sum(1 for a in allocation if a.get("coverage", 0) >= 80)
            
            # Generate summary using LLM if available
            prompt = f"""
            Please provide a brief summary of the following inventory allocation for {product.name}:
            
            Total Available Stock: {total_stock} units
            Total Projected Demand: {total_demand} units
            Overall Coverage: {coverage_pct}%
            Allocation Strategy: {allocation_strategy}
            Stores with Low Coverage (<80%): {low_coverage}
            Stores with Good Coverage (≥80%): {good_coverage}
            Total Stores: {len(allocation)}
            
            Provide a brief summary (2-3 sentences) of this allocation and any key insights.
            """
            
            summary = self.analyze_with_llm(prompt)
            
            if not summary:
                # Fallback if LLM is not available
                if coverage_pct >= 100:
                    summary = (
                        f"The available {total_stock} units of {product.name} are sufficient to cover the projected demand "
                        f"of {total_demand} units across all {len(allocation)} stores, with {coverage_pct}% overall coverage. "
                        f"All stores can receive their full projected demand amounts, allowing for optimal inventory levels "
                        f"throughout the distribution network."
                    )
                elif coverage_pct >= 80:
                    summary = (
                        f"The available {total_stock} units of {product.name} provide {coverage_pct}% coverage of the projected "
                        f"demand of {total_demand} units across all {len(allocation)} stores. While not all demand can be met, "
                        f"the allocation strategy ensures that {good_coverage} stores maintain good coverage levels, with only "
                        f"{low_coverage} stores falling below 80% coverage. Consider increasing total inventory if possible."
                    )
                else:
                    summary = (
                        f"ALERT: The available {total_stock} units of {product.name} can only cover {coverage_pct}% of the projected "
                        f"demand of {total_demand} units across {len(allocation)} stores. This shortage results in {low_coverage} stores "
                        f"having inadequate coverage below 80%. Urgent action is needed to secure additional inventory or prioritize "
                        f"high-value or strategic locations."
                    )
            
            return summary
        
        except Exception as e:
            logger.error(f"Error generating allocation summary: {str(e)}")
            return "Error generating summary"